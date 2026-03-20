"""
URL configuration for hr_system project.

This file contains all the URL routes for the HR Management System.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # API Routes
    path('api/auth/', include('authentication.urls')),
    path('api/employees/', include('employees.urls')),
    path('api/departments/', include('departments.urls')),
    path('api/attendance/', include('attendance.urls')),
    path('api/leave/', include('leave_management.urls')),
    path('api/payroll/', include('payroll.urls')),
    path('api/recruitment/', include('recruitment.urls')),
    path('api/performance/', include('performance.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
