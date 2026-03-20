from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from employees.views import EmployeeViewSet, EducationRecordViewSet, WorkExperienceViewSet
from authentication import views as auth_views

# Create router
router = DefaultRouter()

# Register viewsets
router.register(r'employees', EmployeeViewSet, basename='employee')
router.register(r'education-records', EducationRecordViewSet, basename='education-record')
router.register(r'work-experiences', WorkExperienceViewSet, basename='work-experience')

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Authentication endpoints
    path('api/auth/login/', auth_views.login, name='login'),
    path('api/auth/register/', auth_views.register, name='register'),
    path('api/auth/logout/', auth_views.logout, name='logout'),
    path('api/auth/profile/', auth_views.user_profile, name='user-profile'),
    path('api/auth/profile/update/', auth_views.update_profile, name='update-profile'),
    path('api/auth/change-password/', auth_views.change_password, name='change-password'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    
    # API endpoints
    path('api/', include(router.urls)),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)