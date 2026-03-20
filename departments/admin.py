from django.contrib import admin
from .models import Department, Position


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name', 'description']
    ordering = ['name']


@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ['title', 'level', 'get_department', 'created_at']
    list_filter = ['level', 'department']
    search_fields = ['title', 'description']
    ordering = ['title']
    
    def get_department(self, obj):
        try:
            return obj.department.name if obj.department else ''
        except:
            return ''
    get_department.short_description = 'Department'
