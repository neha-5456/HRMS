from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PayrollPeriodViewSet, PayslipViewSet, AllowanceViewSet,
    BonusViewSet, TaxBracketViewSet, ProcessPayrollView,
    GeneratePayslipsView, PayrollStatsView
)

router = DefaultRouter()
router.register(r'periods', PayrollPeriodViewSet, basename='payroll-periods')
router.register(r'payslips', PayslipViewSet, basename='payslips')
router.register(r'allowances', AllowanceViewSet, basename='allowances')
router.register(r'bonuses', BonusViewSet, basename='bonuses')
router.register(r'tax-brackets', TaxBracketViewSet, basename='tax-brackets')

urlpatterns = [
    path('', include(router.urls)),
    path('process/', ProcessPayrollView.as_view(), name='process-payroll'),
    path('generate/', GeneratePayslipsView.as_view(), name='generate-payslips'),
    path('stats/', PayrollStatsView.as_view(), name='payroll-stats'),
]
