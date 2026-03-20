from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q

from .models import Department, Position
from .serializers import DepartmentSerializer, PositionSerializer


class DepartmentViewSet(viewsets.ModelViewSet):
    """ViewSet for Department CRUD operations"""
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = Department.objects.all()
        
        # Filter by is_active
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            if is_active.lower() in ['true', '1', 'yes']:
                queryset = queryset.filter(is_active=True)
        
        # Search
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search)
            )
        
        return queryset.order_by('name')
    
    @action(detail=True, methods=['get'])
    def positions(self, request, pk=None):
        """Get all positions in a department"""
        department = self.get_object()
        positions = Position.objects.filter(department=department)
        serializer = PositionSerializer(positions, many=True)
        return Response(serializer.data)


class PositionViewSet(viewsets.ModelViewSet):
    """ViewSet for Position CRUD operations"""
    queryset = Position.objects.select_related('department')
    serializer_class = PositionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = Position.objects.select_related('department')
        
        # Filter by department
        department_id = self.request.query_params.get('department_id')
        if department_id:
            queryset = queryset.filter(department_id=department_id)
        
        # Search
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search)
            )
        
        return queryset.order_by('title')
