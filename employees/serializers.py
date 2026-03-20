from rest_framework import serializers
from .models import Employee


class EmployeeListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing employees"""
    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    department_name = serializers.SerializerMethodField()
    position_title = serializers.SerializerMethodField()
    
    class Meta:
        model = Employee
        fields = [
            'id', 'employee_id', 'first_name', 'last_name', 'full_name',
            'email', 'personal_email', 'department_id', 'department_name',
            'position_id', 'position_title', 'employment_type', 'is_active',
            'date_of_joining', 'city', 'country', 'basic_salary'
        ]
    
    def get_first_name(self, obj):
        try:
            return obj.user.first_name if obj.user else ''
        except:
            return ''
    
    def get_last_name(self, obj):
        try:
            return obj.user.last_name if obj.user else ''
        except:
            return ''
    
    def get_full_name(self, obj):
        try:
            if obj.user:
                return f"{obj.user.first_name} {obj.user.last_name}".strip()
            return obj.employee_id
        except:
            return obj.employee_id
    
    def get_email(self, obj):
        return obj.personal_email
    
    def get_department_name(self, obj):
        try:
            return obj.department.name if obj.department else None
        except:
            return None
    
    def get_position_title(self, obj):
        try:
            return obj.position.title if obj.position else None
        except:
            return None


class EmployeeDetailSerializer(serializers.ModelSerializer):
    """Full serializer for employee details"""
    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    department_name = serializers.SerializerMethodField()
    position_title = serializers.SerializerMethodField()
    manager_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Employee
        fields = [
            'id', 'employee_id', 'first_name', 'last_name', 'full_name',
            'email', 'personal_email', 'date_of_birth', 'gender', 'marital_status',
            'nationality', 'address_line1', 'address_line2', 'city', 'state',
            'postal_code', 'country', 'department_id', 'department_name',
            'position_id', 'position_title', 'manager_id', 'manager_name',
            'employment_type', 'date_of_joining', 'date_of_leaving',
            'probation_period_months', 'notice_period_days', 'basic_salary',
            'currency', 'resume', 'id_document', 'is_active',
            'emergency_contact_name', 'emergency_contact_phone',
            'emergency_contact_relation', 'created_at', 'updated_at'
        ]
    
    def get_first_name(self, obj):
        try:
            return obj.user.first_name if obj.user else ''
        except:
            return ''
    
    def get_last_name(self, obj):
        try:
            return obj.user.last_name if obj.user else ''
        except:
            return ''
    
    def get_full_name(self, obj):
        try:
            if obj.user:
                return f"{obj.user.first_name} {obj.user.last_name}".strip()
            return obj.employee_id
        except:
            return obj.employee_id
    
    def get_email(self, obj):
        return obj.personal_email
    
    def get_department_name(self, obj):
        try:
            return obj.department.name if obj.department else None
        except:
            return None
    
    def get_position_title(self, obj):
        try:
            return obj.position.title if obj.position else None
        except:
            return None
    
    def get_manager_name(self, obj):
        try:
            if obj.manager and obj.manager.user:
                return f"{obj.manager.user.first_name} {obj.manager.user.last_name}".strip()
        except:
            pass
        return None


class EmployeeCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating employees"""
    class Meta:
        model = Employee
        fields = [
            'employee_id', 'date_of_birth', 'gender', 'marital_status',
            'nationality', 'personal_email', 'address_line1', 'address_line2',
            'city', 'state', 'postal_code', 'country', 'department', 'position',
            'manager', 'employment_type', 'date_of_joining', 'date_of_leaving',
            'probation_period_months', 'notice_period_days', 'basic_salary',
            'currency', 'resume', 'id_document', 'is_active',
            'emergency_contact_name', 'emergency_contact_phone',
            'emergency_contact_relation'
        ]
