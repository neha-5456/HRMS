from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Count

from .models import Employee
from .serializers import (
    EmployeeListSerializer, EmployeeDetailSerializer, EmployeeCreateSerializer
)


class EmployeeViewSet(viewsets.ModelViewSet):
    """ViewSet for Employee CRUD operations"""
    queryset = Employee.objects.select_related('user', 'department', 'position', 'manager', 'manager__user')
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return EmployeeListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return EmployeeCreateSerializer
        return EmployeeDetailSerializer
    
    def get_queryset(self):
        queryset = Employee.objects.select_related('user', 'department', 'position', 'manager', 'manager__user')
        
        # Search by user's first/last name or employee_id
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(user__first_name__icontains=search) |
                Q(user__last_name__icontains=search) |
                Q(personal_email__icontains=search) |
                Q(employee_id__icontains=search)
            )
        
        # Filter by department
        department_id = self.request.query_params.get('department_id')
        if department_id:
            queryset = queryset.filter(department_id=department_id)
        
        # Filter by is_active status
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            if is_active.lower() in ['true', '1', 'yes']:
                queryset = queryset.filter(is_active=True)
            elif is_active.lower() in ['false', '0', 'no']:
                queryset = queryset.filter(is_active=False)
        
        # Filter by employment type
        employment_type = self.request.query_params.get('employment_type')
        if employment_type:
            queryset = queryset.filter(employment_type=employment_type.upper())
        
        # Filter by manager
        manager_id = self.request.query_params.get('manager_id')
        if manager_id:
            queryset = queryset.filter(manager_id=manager_id)
        
        return queryset.order_by('employee_id')
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get employee statistics"""
        total = Employee.objects.count()
        active = Employee.objects.filter(is_active=True).count()
        inactive = total - active
        
        by_department = Employee.objects.values(
            'department__name'
        ).annotate(
            count=Count('id')
        ).order_by('-count')
        
        by_type = Employee.objects.values(
            'employment_type'
        ).annotate(
            count=Count('id')
        )
        
        return Response({
            'total': total,
            'active': active,
            'inactive': inactive,
            'by_department': list(by_department),
            'by_type': list(by_type)
        })
    
    @action(detail=True, methods=['get'])
    def direct_reports(self, request, pk=None):
        """Get direct reports for a manager"""
        employee = self.get_object()
        reports = Employee.objects.filter(manager=employee).select_related('user', 'department', 'position')
        serializer = EmployeeListSerializer(reports, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Activate an employee"""
        employee = self.get_object()
        employee.is_active = True
        employee.save()
        return Response({'message': 'Employee activated'})
    
    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """Deactivate an employee"""
        employee = self.get_object()
        employee.is_active = False
        employee.save()
        return Response({'message': 'Employee deactivated'})
