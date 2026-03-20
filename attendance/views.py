from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.db.models import Count, Q
from django.utils import timezone
from datetime import datetime, timedelta

from .models import Attendance, Holiday, WorkSchedule
from .serializers import (
    AttendanceSerializer, AttendanceCreateSerializer, BulkAttendanceSerializer,
    HolidaySerializer, WorkScheduleSerializer, AttendanceSummarySerializer
)
from employees.models import Employee


class AttendanceViewSet(viewsets.ModelViewSet):
    """ViewSet for Attendance CRUD operations"""
    queryset = Attendance.objects.all().select_related('employee', 'employee__department')
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return AttendanceCreateSerializer
        return AttendanceSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by date
        date = self.request.query_params.get('date')
        if date:
            queryset = queryset.filter(date=date)
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if start_date and end_date:
            queryset = queryset.filter(date__range=[start_date, end_date])
        
        # Filter by employee
        employee_id = self.request.query_params.get('employee_id')
        if employee_id:
            queryset = queryset.filter(employee_id=employee_id)
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by department
        department_id = self.request.query_params.get('department_id')
        if department_id:
            queryset = queryset.filter(employee__department_id=department_id)
        
        return queryset.order_by('-date', 'employee__first_name')
    
    @action(detail=False, methods=['post'])
    def bulk_mark(self, request):
        """Mark attendance for multiple employees at once"""
        serializer = BulkAttendanceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        date = serializer.validated_data['date']
        employee_ids = serializer.validated_data['employee_ids']
        attendance_status = serializer.validated_data['status']
        check_in = serializer.validated_data.get('check_in_time')
        check_out = serializer.validated_data.get('check_out_time')
        
        created = []
        updated = []
        errors = []
        
        for emp_id in employee_ids:
            try:
                employee = Employee.objects.get(id=emp_id)
                attendance, was_created = Attendance.objects.update_or_create(
                    employee=employee,
                    date=date,
                    defaults={
                        'status': attendance_status,
                        'check_in_time': check_in,
                        'check_out_time': check_out,
                    }
                )
                
                if was_created:
                    created.append(emp_id)
                else:
                    updated.append(emp_id)
                    
            except Employee.DoesNotExist:
                errors.append({'employee_id': emp_id, 'error': 'Employee not found'})
            except Exception as e:
                errors.append({'employee_id': emp_id, 'error': str(e)})
        
        return Response({
            'message': f'Attendance marked for {len(created) + len(updated)} employees',
            'created': len(created),
            'updated': len(updated),
            'errors': errors
        })
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get attendance summary for a specific date"""
        date = request.query_params.get('date', timezone.now().date().isoformat())
        
        # Get all active employees
        total_employees = Employee.objects.filter(employment_status='ACTIVE').count()
        
        # Get attendance stats for the date
        attendance_stats = Attendance.objects.filter(date=date).values('status').annotate(
            count=Count('id')
        )
        
        stats = {item['status']: item['count'] for item in attendance_stats}
        marked_count = sum(stats.values())
        
        return Response({
            'date': date,
            'total_employees': total_employees,
            'present': stats.get('PRESENT', 0),
            'absent': stats.get('ABSENT', 0),
            'late': stats.get('LATE', 0),
            'half_day': stats.get('HALF_DAY', 0),
            'on_leave': stats.get('ON_LEAVE', 0),
            'not_marked': total_employees - marked_count
        })
    
    @action(detail=False, methods=['get'])
    def today(self, request):
        """Get today's attendance"""
        today = timezone.now().date()
        queryset = self.get_queryset().filter(date=today)
        serializer = AttendanceSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def check_in(self, request):
        """Check in for an employee"""
        employee_id = request.data.get('employee_id')
        if not employee_id:
            return Response(
                {'error': 'employee_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            employee = Employee.objects.get(id=employee_id)
        except Employee.DoesNotExist:
            return Response(
                {'error': 'Employee not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        today = timezone.now().date()
        now = timezone.now().time()
        
        attendance, created = Attendance.objects.get_or_create(
            employee=employee,
            date=today,
            defaults={
                'check_in_time': now,
                'status': 'PRESENT'
            }
        )
        
        if not created and attendance.check_in_time:
            return Response(
                {'error': 'Already checked in today'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not created:
            attendance.check_in_time = now
            attendance.status = 'PRESENT'
            attendance.save()
        
        serializer = AttendanceSerializer(attendance)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def check_out(self, request):
        """Check out for an employee"""
        employee_id = request.data.get('employee_id')
        if not employee_id:
            return Response(
                {'error': 'employee_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            employee = Employee.objects.get(id=employee_id)
        except Employee.DoesNotExist:
            return Response(
                {'error': 'Employee not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        today = timezone.now().date()
        now = timezone.now().time()
        
        try:
            attendance = Attendance.objects.get(employee=employee, date=today)
        except Attendance.DoesNotExist:
            return Response(
                {'error': 'No check-in record found for today'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if attendance.check_out_time:
            return Response(
                {'error': 'Already checked out today'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        attendance.check_out_time = now
        
        # Calculate work hours
        if attendance.check_in_time:
            check_in = datetime.combine(today, attendance.check_in_time)
            check_out = datetime.combine(today, now)
            work_duration = check_out - check_in
            attendance.work_hours = work_duration.total_seconds() / 3600  # Convert to hours
        
        attendance.save()
        
        serializer = AttendanceSerializer(attendance)
        return Response(serializer.data)


class HolidayViewSet(viewsets.ModelViewSet):
    """ViewSet for Holiday CRUD operations"""
    queryset = Holiday.objects.all()
    serializer_class = HolidaySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by year
        year = self.request.query_params.get('year')
        if year:
            queryset = queryset.filter(date__year=year)
        
        # Filter by type
        holiday_type = self.request.query_params.get('type')
        if holiday_type:
            queryset = queryset.filter(holiday_type=holiday_type)
        
        return queryset.order_by('date')
    
    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Get upcoming holidays"""
        today = timezone.now().date()
        holidays = Holiday.objects.filter(date__gte=today).order_by('date')[:10]
        serializer = HolidaySerializer(holidays, many=True)
        return Response(serializer.data)


class WorkScheduleViewSet(viewsets.ModelViewSet):
    """ViewSet for WorkSchedule CRUD operations"""
    queryset = WorkSchedule.objects.all().select_related('employee')
    serializer_class = WorkScheduleSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by employee
        employee_id = self.request.query_params.get('employee_id')
        if employee_id:
            queryset = queryset.filter(employee_id=employee_id)
        
        return queryset.order_by('day_of_week')


class AttendanceReportView(APIView):
    """Generate attendance reports"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        employee_id = request.query_params.get('employee_id')
        department_id = request.query_params.get('department_id')
        
        if not start_date or not end_date:
            # Default to current month
            today = timezone.now().date()
            start_date = today.replace(day=1)
            end_date = today
        
        queryset = Attendance.objects.filter(
            date__range=[start_date, end_date]
        ).select_related('employee', 'employee__department')
        
        if employee_id:
            queryset = queryset.filter(employee_id=employee_id)
        
        if department_id:
            queryset = queryset.filter(employee__department_id=department_id)
        
        # Aggregate stats
        stats = queryset.values('status').annotate(count=Count('id'))
        stats_dict = {item['status']: item['count'] for item in stats}
        
        # Get employee-wise summary
        employee_stats = queryset.values(
            'employee__id',
            'employee__first_name',
            'employee__last_name',
            'employee__employee_id'
        ).annotate(
            present=Count('id', filter=Q(status='PRESENT')),
            absent=Count('id', filter=Q(status='ABSENT')),
            late=Count('id', filter=Q(status='LATE')),
            half_day=Count('id', filter=Q(status='HALF_DAY')),
            on_leave=Count('id', filter=Q(status='ON_LEAVE')),
            total=Count('id')
        )
        
        return Response({
            'period': {
                'start_date': start_date,
                'end_date': end_date
            },
            'summary': {
                'present': stats_dict.get('PRESENT', 0),
                'absent': stats_dict.get('ABSENT', 0),
                'late': stats_dict.get('LATE', 0),
                'half_day': stats_dict.get('HALF_DAY', 0),
                'on_leave': stats_dict.get('ON_LEAVE', 0),
                'total_records': sum(stats_dict.values())
            },
            'employee_stats': list(employee_stats)
        })
