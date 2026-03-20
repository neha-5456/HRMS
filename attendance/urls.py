from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AttendanceViewSet, HolidayViewSet, WorkScheduleViewSet,
    AttendanceReportView
)

router = DefaultRouter()
router.register(r'records', AttendanceViewSet, basename='attendance')
router.register(r'holidays', HolidayViewSet, basename='holidays')
router.register(r'schedules', WorkScheduleViewSet, basename='work-schedules')

urlpatterns = [
    path('', include(router.urls)),
    path('report/', AttendanceReportView.as_view(), name='attendance-report'),
    
    # Convenience aliases for common operations
    path('mark/', AttendanceViewSet.as_view({'post': 'create'}), name='mark-attendance'),
    path('bulk/', AttendanceViewSet.as_view({'post': 'bulk_mark'}), name='bulk-attendance'),
    path('summary/', AttendanceViewSet.as_view({'get': 'summary'}), name='attendance-summary'),
    path('today/', AttendanceViewSet.as_view({'get': 'today'}), name='today-attendance'),
    path('check-in/', AttendanceViewSet.as_view({'post': 'check_in'}), name='check-in'),
    path('check-out/', AttendanceViewSet.as_view({'post': 'check_out'}), name='check-out'),
]
