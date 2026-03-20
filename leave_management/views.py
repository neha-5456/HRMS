from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.db.models import Sum, Q
from django.utils import timezone
from datetime import datetime

from .models import LeaveType, LeaveBalance, LeaveRequest
from .serializers import (
    LeaveTypeSerializer, LeaveBalanceSerializer, LeaveRequestSerializer,
    LeaveRequestCreateSerializer, LeaveApprovalSerializer
)
from employees.models import Employee


class LeaveTypeViewSet(viewsets.ModelViewSet):
    """ViewSet for LeaveType CRUD operations"""
    queryset = LeaveType.objects.all()
    serializer_class = LeaveTypeSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        return queryset.order_by('name')


class LeaveBalanceViewSet(viewsets.ModelViewSet):
    """ViewSet for LeaveBalance CRUD operations"""
    queryset = LeaveBalance.objects.all().select_related('employee', 'leave_type')
    serializer_class = LeaveBalanceSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by employee
        employee_id = self.request.query_params.get('employee_id')
        if employee_id:
            queryset = queryset.filter(employee_id=employee_id)
        
        # Filter by year
        year = self.request.query_params.get('year')
        if year:
            queryset = queryset.filter(year=year)
        else:
            # Default to current year
            queryset = queryset.filter(year=timezone.now().year)
        
        # Filter by leave type
        leave_type_id = self.request.query_params.get('leave_type_id')
        if leave_type_id:
            queryset = queryset.filter(leave_type_id=leave_type_id)
        
        return queryset.order_by('employee__first_name', 'leave_type__name')
    
    @action(detail=False, methods=['get'])
    def my_balance(self, request):
        """Get leave balance for the authenticated user"""
        user = request.user
        year = request.query_params.get('year', timezone.now().year)
        
        # Try to find employee linked to user
        try:
            employee = Employee.objects.get(user=user)
        except Employee.DoesNotExist:
            return Response(
                {'error': 'No employee profile found for this user'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        balances = LeaveBalance.objects.filter(
            employee=employee,
            year=year
        ).select_related('leave_type')
        
        serializer = LeaveBalanceSerializer(balances, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def initialize(self, request):
        """Initialize leave balances for all employees for a year"""
        year = request.data.get('year', timezone.now().year)
        
        employees = Employee.objects.filter(employment_status='ACTIVE')
        leave_types = LeaveType.objects.filter(is_active=True)
        
        created_count = 0
        for employee in employees:
            for leave_type in leave_types:
                balance, created = LeaveBalance.objects.get_or_create(
                    employee=employee,
                    leave_type=leave_type,
                    year=year,
                    defaults={
                        'total_days': leave_type.days_allowed,
                        'used_days': 0,
                        'pending_days': 0,
                        'carried_forward': 0
                    }
                )
                if created:
                    created_count += 1
        
        return Response({
            'message': f'Initialized {created_count} leave balance records for {year}',
            'year': year
        })


class LeaveRequestViewSet(viewsets.ModelViewSet):
    """ViewSet for LeaveRequest CRUD operations"""
    queryset = LeaveRequest.objects.all().select_related(
        'employee', 'employee__department', 'leave_type', 'approved_by'
    )
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return LeaveRequestCreateSerializer
        return LeaveRequestSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by employee
        employee_id = self.request.query_params.get('employee_id')
        if employee_id:
            queryset = queryset.filter(employee_id=employee_id)
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by leave type
        leave_type_id = self.request.query_params.get('leave_type_id')
        if leave_type_id:
            queryset = queryset.filter(leave_type_id=leave_type_id)
        
        # Filter by department
        department_id = self.request.query_params.get('department_id')
        if department_id:
            queryset = queryset.filter(employee__department_id=department_id)
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if start_date and end_date:
            queryset = queryset.filter(
                Q(start_date__range=[start_date, end_date]) |
                Q(end_date__range=[start_date, end_date])
            )
        
        return queryset.order_by('-created_at')
    
    def perform_create(self, serializer):
        leave_request = serializer.save(status='PENDING')
        
        # Update pending days in leave balance
        employee = leave_request.employee
        leave_type = leave_request.leave_type
        year = leave_request.start_date.year
        
        # Calculate days
        if leave_request.is_half_day:
            days = 0.5
        else:
            days = (leave_request.end_date - leave_request.start_date).days + 1
        
        try:
            balance = LeaveBalance.objects.get(
                employee=employee,
                leave_type=leave_type,
                year=year
            )
            balance.pending_days += days
            balance.save()
        except LeaveBalance.DoesNotExist:
            pass
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve a leave request"""
        leave_request = self.get_object()
        
        if leave_request.status != 'PENDING':
            return Response(
                {'error': 'Can only approve pending requests'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        leave_request.status = 'APPROVED'
        leave_request.approved_by = request.user
        leave_request.approved_date = timezone.now()
        leave_request.save()
        
        # Update leave balance
        self._update_balance_on_approval(leave_request)
        
        serializer = LeaveRequestSerializer(leave_request)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Reject a leave request"""
        leave_request = self.get_object()
        
        if leave_request.status != 'PENDING':
            return Response(
                {'error': 'Can only reject pending requests'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        rejection_reason = request.data.get('rejection_reason', '')
        
        leave_request.status = 'REJECTED'
        leave_request.approved_by = request.user
        leave_request.approved_date = timezone.now()
        leave_request.rejection_reason = rejection_reason
        leave_request.save()
        
        # Revert pending days
        self._revert_pending_days(leave_request)
        
        serializer = LeaveRequestSerializer(leave_request)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel a leave request"""
        leave_request = self.get_object()
        
        if leave_request.status not in ['PENDING', 'APPROVED']:
            return Response(
                {'error': 'Can only cancel pending or approved requests'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        old_status = leave_request.status
        leave_request.status = 'CANCELLED'
        leave_request.save()
        
        # Revert balance changes
        if old_status == 'PENDING':
            self._revert_pending_days(leave_request)
        elif old_status == 'APPROVED':
            self._revert_approved_days(leave_request)
        
        serializer = LeaveRequestSerializer(leave_request)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def pending(self, request):
        """Get all pending leave requests"""
        queryset = self.get_queryset().filter(status='PENDING')
        serializer = LeaveRequestSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def my_requests(self, request):
        """Get leave requests for the authenticated user"""
        user = request.user
        
        try:
            employee = Employee.objects.get(user=user)
        except Employee.DoesNotExist:
            return Response(
                {'error': 'No employee profile found for this user'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        queryset = self.get_queryset().filter(employee=employee)
        serializer = LeaveRequestSerializer(queryset, many=True)
        return Response(serializer.data)
    
    def _calculate_days(self, leave_request):
        """Calculate number of leave days"""
        if leave_request.is_half_day:
            return 0.5
        return (leave_request.end_date - leave_request.start_date).days + 1
    
    def _update_balance_on_approval(self, leave_request):
        """Update leave balance when request is approved"""
        days = self._calculate_days(leave_request)
        year = leave_request.start_date.year
        
        try:
            balance = LeaveBalance.objects.get(
                employee=leave_request.employee,
                leave_type=leave_request.leave_type,
                year=year
            )
            balance.pending_days -= days
            balance.used_days += days
            balance.save()
        except LeaveBalance.DoesNotExist:
            pass
    
    def _revert_pending_days(self, leave_request):
        """Revert pending days when request is rejected/cancelled"""
        days = self._calculate_days(leave_request)
        year = leave_request.start_date.year
        
        try:
            balance = LeaveBalance.objects.get(
                employee=leave_request.employee,
                leave_type=leave_request.leave_type,
                year=year
            )
            balance.pending_days -= days
            balance.save()
        except LeaveBalance.DoesNotExist:
            pass
    
    def _revert_approved_days(self, leave_request):
        """Revert used days when approved request is cancelled"""
        days = self._calculate_days(leave_request)
        year = leave_request.start_date.year
        
        try:
            balance = LeaveBalance.objects.get(
                employee=leave_request.employee,
                leave_type=leave_request.leave_type,
                year=year
            )
            balance.used_days -= days
            balance.save()
        except LeaveBalance.DoesNotExist:
            pass


class LeaveStatsView(APIView):
    """Get leave statistics"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        today = timezone.now().date()
        
        # Count employees on leave today
        on_leave_today = LeaveRequest.objects.filter(
            status='APPROVED',
            start_date__lte=today,
            end_date__gte=today
        ).count()
        
        # Pending requests count
        pending_requests = LeaveRequest.objects.filter(status='PENDING').count()
        
        # This month stats
        month_start = today.replace(day=1)
        approved_this_month = LeaveRequest.objects.filter(
            status='APPROVED',
            approved_date__gte=month_start
        ).count()
        
        return Response({
            'on_leave_today': on_leave_today,
            'pending_requests': pending_requests,
            'approved_this_month': approved_this_month,
            'date': today.isoformat()
        })
