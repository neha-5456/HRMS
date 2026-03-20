from rest_framework import serializers
from .models import Attendance, Holiday, WorkSchedule
from employees.models import Employee


class AttendanceSerializer(serializers.ModelSerializer):
    employee_name = serializers.SerializerMethodField()
    employee_id_display = serializers.SerializerMethodField()
    department_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Attendance
        fields = [
            'id', 'employee', 'employee_name', 'employee_id_display', 'department_name',
            'date', 'check_in_time', 'check_out_time', 'status', 'work_hours',
            'overtime_hours', 'notes', 'is_remote', 'location',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'work_hours']
    
    def get_employee_name(self, obj):
        return f"{obj.employee.first_name} {obj.employee.last_name}"
    
    def get_employee_id_display(self, obj):
        return obj.employee.employee_id
    
    def get_department_name(self, obj):
        if obj.employee.department:
            return obj.employee.department.name
        return None


class AttendanceCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = [
            'employee', 'date', 'check_in_time', 'check_out_time',
            'status', 'overtime_hours', 'notes', 'is_remote', 'location'
        ]
    
    def validate(self, data):
        # Check for duplicate attendance
        employee = data.get('employee')
        date = data.get('date')
        
        if self.instance is None:  # Creating new record
            if Attendance.objects.filter(employee=employee, date=date).exists():
                raise serializers.ValidationError(
                    "Attendance record already exists for this employee on this date."
                )
        return data


class BulkAttendanceSerializer(serializers.Serializer):
    """Serializer for bulk attendance marking"""
    date = serializers.DateField(required=True)
    employee_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=True
    )
    status = serializers.ChoiceField(
        choices=['PRESENT', 'ABSENT', 'LATE', 'HALF_DAY', 'ON_LEAVE'],
        required=True
    )
    check_in_time = serializers.TimeField(required=False, allow_null=True)
    check_out_time = serializers.TimeField(required=False, allow_null=True)


class HolidaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Holiday
        fields = [
            'id', 'name', 'date', 'description', 'is_recurring',
            'holiday_type', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class WorkScheduleSerializer(serializers.ModelSerializer):
    employee_name = serializers.SerializerMethodField()
    
    class Meta:
        model = WorkSchedule
        fields = [
            'id', 'employee', 'employee_name', 'day_of_week',
            'start_time', 'end_time', 'is_working_day',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_employee_name(self, obj):
        if obj.employee:
            return f"{obj.employee.first_name} {obj.employee.last_name}"
        return "Default Schedule"


class AttendanceSummarySerializer(serializers.Serializer):
    """Serializer for attendance summary response"""
    date = serializers.DateField()
    total_employees = serializers.IntegerField()
    present = serializers.IntegerField()
    absent = serializers.IntegerField()
    late = serializers.IntegerField()
    half_day = serializers.IntegerField()
    on_leave = serializers.IntegerField()
    not_marked = serializers.IntegerField()
