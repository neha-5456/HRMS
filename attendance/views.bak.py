from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from .models import Attendance
from .serializers import AttendanceSerializer

class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = Attendance.objects.select_related('employee')
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
            
        # Filter by employee
        employee_id = self.request.query_params.get('employee_id')
        if employee_id:
            queryset = queryset.filter(employee_id=employee_id)
            
        return queryset.order_by('-date')
    
    @action(detail=False, methods=['post'])
    def check_in(self, request):
        """Mark check-in for current user"""
        employee = request.user.employee_profile
        today = timezone.now().date()
        
        attendance, created = Attendance.objects.get_or_create(
            employee=employee,
            date=today,
            defaults={'check_in': timezone.now(), 'status': 'PRESENT'}
        )
        
        if not created and attendance.check_in:
            return Response(
                {'error': 'Already checked in today'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        attendance.check_in = timezone.now()
        attendance.status = 'PRESENT'
        attendance.save()
        
        serializer = self.get_serializer(attendance)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def check_out(self, request):
        """Mark check-out for current user"""
        employee = request.user.employee_profile
        today = timezone.now().date()
        
        try:
            attendance = Attendance.objects.get(employee=employee, date=today)
        except Attendance.DoesNotExist:
            return Response(
                {'error': 'No check-in record found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if attendance.check_out:
            return Response(
                {'error': 'Already checked out'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        attendance.check_out = timezone.now()
        attendance.save()
        
        serializer = self.get_serializer(attendance)
        return Response(serializer.data)