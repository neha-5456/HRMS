from django.contrib import admin
from .models import Employee


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = [
        'employee_id', 'get_first_name', 'get_last_name', 'personal_email',
        'get_department', 'employment_type', 'is_active', 'date_of_joining'
    ]
    list_filter = [
        'is_active', 'employment_type', 'gender', 'department'
    ]
    search_fields = [
        'employee_id', 'personal_email', 'user__first_name', 'user__last_name'
    ]
    ordering = ['employee_id']
    list_per_page = 25
    raw_id_fields = ['user', 'manager']
    
    def get_first_name(self, obj):
        try:
            return obj.user.first_name if obj.user else ''
        except:
            return ''
    get_first_name.short_description = 'First Name'
    get_first_name.admin_order_field = 'user__first_name'
    
    def get_last_name(self, obj):
        try:
            return obj.user.last_name if obj.user else ''
        except:
            return ''
    get_last_name.short_description = 'Last Name'
    get_last_name.admin_order_field = 'user__last_name'
    
    def get_department(self, obj):
        try:
            return obj.department.name if obj.department else ''
        except:
            return ''
    get_department.short_description = 'Department'
    get_department.admin_order_field = 'department__name'
