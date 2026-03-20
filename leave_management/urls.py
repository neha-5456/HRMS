from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    LeaveTypeViewSet, LeaveBalanceViewSet, LeaveRequestViewSet,
    LeaveStatsView
)

router = DefaultRouter()
router.register(r'types', LeaveTypeViewSet, basename='leave-types')
router.register(r'balances', LeaveBalanceViewSet, basename='leave-balances')
router.register(r'requests', LeaveRequestViewSet, basename='leave-requests')

urlpatterns = [
    path('', include(router.urls)),
    path('stats/', LeaveStatsView.as_view(), name='leave-stats'),
    
    # Convenience aliases
    path('pending/', LeaveRequestViewSet.as_view({'get': 'pending'}), name='pending-requests'),
    path('apply/', LeaveRequestViewSet.as_view({'post': 'create'}), name='apply-leave'),
]
