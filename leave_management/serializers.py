from rest_framework import serializers
from .models import LeaveType, LeaveBalance, LeaveRequest
from employees.models import Employee


class LeaveTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveType
        fields = [
            'id', 'name', 'code', 'description', 'days_allowed',
            'is_paid', 'is_carry_forward', 'max_carry_forward_days',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class LeaveBalanceSerializer(serializers.ModelSerializer):
    employee_name = serializers.SerializerMethodField()
    leave_type_name = serializers.SerializerMethodField()
    available_days = serializers.SerializerMethodField()
    
    class Meta:
        model = LeaveBalance
        fields = [
            'id', 'employee', 'employee_name', 'leave_type', 'leave_type_name',
            'year', 'total_days', 'used_days', 'pending_days', 'carried_forward',
            'available_days', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_employee_name(self, obj):
        return f"{obj.employee.first_name} {obj.employee.last_name}"
    
    def get_leave_type_name(self, obj):
        return obj.leave_type.name
    
    def get_available_days(self, obj):
        return obj.total_days + obj.carried_forward - obj.used_days - obj.pending_days


class LeaveRequestSerializer(serializers.ModelSerializer):
    employee_name = serializers.SerializerMethodField()
    employee_id_display = serializers.SerializerMethodField()
    department_name = serializers.SerializerMethodField()
    leave_type_name = serializers.SerializerMethodField()
    approved_by_name = serializers.SerializerMethodField()
    duration = serializers.SerializerMethodField()
    
    class Meta:
        model = LeaveRequest
        fields = [
            'id', 'employee', 'employee_name', 'employee_id_display', 'department_name',
            'leave_type', 'leave_type_name', 'start_date', 'end_date', 'duration',
            'reason', 'status', 'approved_by', 'approved_by_name', 'approved_date',
            'rejection_reason', 'is_half_day', 'half_day_type',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'approved_by', 'approved_date']
    
    def get_employee_name(self, obj):
        return f"{obj.employee.first_name} {obj.employee.last_name}"
    
    def get_employee_id_display(self, obj):
        return obj.employee.employee_id
    
    def get_department_name(self, obj):
        if obj.employee.department:
            return obj.employee.department.name
        return None
    
    def get_leave_type_name(self, obj):
        return obj.leave_type.name
    
    def get_approved_by_name(self, obj):
        if obj.approved_by:
            return f"{obj.approved_by.first_name} {obj.approved_by.last_name}"
        return None
    
    def get_duration(self, obj):
        if obj.is_half_day:
            return 0.5
        delta = (obj.end_date - obj.start_date).days + 1
        return delta


class LeaveRequestCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveRequest
        fields = [
            'employee', 'leave_type', 'start_date', 'end_date',
            'reason', 'is_half_day', 'half_day_type'
        ]
    
    def validate(self, data):
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        if start_date and end_date and start_date > end_date:
            raise serializers.ValidationError(
                "End date must be after start date."
            )
        
        # Check for overlapping leave requests
        employee = data.get('employee')
        overlapping = LeaveRequest.objects.filter(
            employee=employee,
            status__in=['PENDING', 'APPROVED'],
            start_date__lte=end_date,
            end_date__gte=start_date
        )
        
        if self.instance:
            overlapping = overlapping.exclude(pk=self.instance.pk)
        
        if overlapping.exists():
            raise serializers.ValidationError(
                "You have overlapping leave requests for these dates."
            )
        
        return data


class LeaveApprovalSerializer(serializers.Serializer):
    """Serializer for leave approval/rejection"""
    action = serializers.ChoiceField(choices=['approve', 'reject'], required=True)
    rejection_reason = serializers.CharField(required=False, allow_blank=True)


class LeaveBalanceSummarySerializer(serializers.Serializer):
    """Serializer for leave balance summary"""
    leave_type = serializers.CharField()
    leave_type_id = serializers.IntegerField()
    total_days = serializers.FloatField()
    used_days = serializers.FloatField()
    pending_days = serializers.FloatField()
    available_days = serializers.FloatField()
