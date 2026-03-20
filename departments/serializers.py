from rest_framework import serializers
from .models import Department, Position


class DepartmentSerializer(serializers.ModelSerializer):
    employee_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Department
        fields = ['id', 'name', 'description', 'is_active', 'manager_id', 
                  'employee_count', 'created_at', 'updated_at']
    
    def get_employee_count(self, obj):
        try:
            return obj.employees.count()
        except:
            return 0


class PositionSerializer(serializers.ModelSerializer):
    department_name = serializers.SerializerMethodField()
    employee_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Position
        fields = ['id', 'title', 'description', 'level', 'department_id',
                  'department_name', 'employee_count', 'created_at', 'updated_at']
    
    def get_department_name(self, obj):
        try:
            return obj.department.name if obj.department else None
        except:
            return None
    
    def get_employee_count(self, obj):
        try:
            return obj.employees.count()
        except:
            return 0
