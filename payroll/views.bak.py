from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum
from .models import Payroll, Salary
from .serializers import PayrollSerializer, SalarySerializer

class PayrollViewSet(viewsets.ModelViewSet):
    queryset = Payroll.objects.all()
    serializer_class = PayrollSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = Payroll.objects.select_related('employee')
        
        # Filter by month/year
        month = self.request.query_params.get('month')
        year = self.request.query_params.get('year')
        
        if month:
            queryset = queryset.filter(month=month)
        if year:
            queryset = queryset.filter(year=year)
        
        return queryset.order_by('-year', '-month')
    
    @action(detail=False, methods=['post'])
    def generate_monthly(self, request):
        """Generate payroll for all employees for a specific month"""
        month = request.data.get('month')
        year = request.data.get('year')
        
        if not month or not year:
            return Response(
                {'error': 'Month and year required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get all active employees with salaries
        from employees.models import Employee
        employees = Employee.objects.filter(status='ACTIVE')
        
        created_count = 0
        for employee in employees:
            try:
                salary = Salary.objects.get(employee=employee, is_active=True)
                
                payroll, created = Payroll.objects.get_or_create(
                    employee=employee,
                    month=month,
                    year=year,
                    defaults={
                        'basic_salary': salary.basic_salary,
                        'allowances': salary.allowances,
                        'deductions': salary.deductions,
                        'net_salary': salary.basic_salary + salary.allowances - salary.deductions,
                        'status': 'PENDING'
                    }
                )
                
                if created:
                    created_count += 1
                    
            except Salary.DoesNotExist:
                continue
        
        return Response({
            'message': f'Generated {created_count} payroll records',
            'month': month,
            'year': year
        })
    
    @action(detail=True, methods=['post'])
    def mark_paid(self, request, pk=None):
        """Mark payroll as paid"""
        payroll = self.get_object()
        payroll.status = 'PAID'
        payroll.save()
        
        serializer = self.get_serializer(payroll)
        return Response(serializer.data)