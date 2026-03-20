from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import LeaveRequest, LeaveBalance, LeaveType
from .serializers import LeaveRequestSerializer, LeaveBalanceSerializer

class LeaveRequestViewSet(viewsets.ModelViewSet):
    queryset = LeaveRequest.objects.all()
    serializer_class = LeaveRequestSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        queryset = LeaveRequest.objects.select_related('employee', 'leave_type')
        
        # Regular employees see only their requests
        if user.role == 'EMPLOYEE':
            queryset = queryset.filter(employee=user.employee_profile)
        
        # Managers see their team's requests
        elif user.role == 'MANAGER':
            queryset = queryset.filter(
                employee__department=user.employee_profile.department
            )
        
        return queryset.order_by('-applied_date')
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve leave request"""
        leave_request = self.get_object()
        
        if request.user.role not in ['MANAGER', 'HR', 'ADMIN']:
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        leave_request.status = 'APPROVED'
        leave_request.approved_by = request.user
        leave_request.save()
        
        serializer = self.get_serializer(leave_request)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Reject leave request"""
        leave_request = self.get_object()
        
        if request.user.role not in ['MANAGER', 'HR', 'ADMIN']:
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        leave_request.status = 'REJECTED'
        leave_request.approved_by = request.user
        leave_request.save()
        
        serializer = self.get_serializer(leave_request)
        return Response(serializer.data)

class LeaveBalanceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = LeaveBalance.objects.all()
    serializer_class = LeaveBalanceSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        
        if user.role == 'EMPLOYEE':
            return LeaveBalance.objects.filter(employee=user.employee_profile)
        
        return LeaveBalance.objects.all()