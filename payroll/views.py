from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import datetime
from decimal import Decimal

from .models import (
    PayrollPeriod, Payslip, PayslipEarning, PayslipDeduction,
    Allowance, Bonus, TaxBracket
)
from .serializers import (
    PayrollPeriodSerializer, PayslipSerializer, PayslipCreateSerializer,
    AllowanceSerializer, BonusSerializer, TaxBracketSerializer,
    ProcessPayrollSerializer, GeneratePayslipSerializer, PayrollSummarySerializer
)
from employees.models import Employee


class PayrollPeriodViewSet(viewsets.ModelViewSet):
    """ViewSet for PayrollPeriod CRUD operations"""
    queryset = PayrollPeriod.objects.all().order_by('-start_date')
    serializer_class = PayrollPeriodSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        status_filter = self.request.query_params.get('status')
        year = self.request.query_params.get('year')
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if year:
            queryset = queryset.filter(start_date__year=year)
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def close_period(self, request, pk=None):
        """Close a payroll period"""
        period = self.get_object()
        if period.status == 'CLOSED':
            return Response(
                {'error': 'Period is already closed'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        period.status = 'CLOSED'
        period.save()
        return Response({'message': 'Period closed successfully'})


class PayslipViewSet(viewsets.ModelViewSet):
    """ViewSet for Payslip CRUD operations"""
    queryset = Payslip.objects.all().select_related('employee', 'employee__department', 'payroll_period')
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return PayslipCreateSerializer
        return PayslipSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by month (YYYY-MM format)
        month = self.request.query_params.get('month')
        if month:
            try:
                year, month_num = month.split('-')
                queryset = queryset.filter(
                    payroll_period__start_date__year=year,
                    payroll_period__start_date__month=month_num
                )
            except ValueError:
                pass
        
        # Filter by employee
        employee_id = self.request.query_params.get('employee_id')
        if employee_id:
            queryset = queryset.filter(employee_id=employee_id)
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by department
        department_id = self.request.query_params.get('department_id')
        if department_id:
            queryset = queryset.filter(employee__department_id=department_id)
        
        return queryset.order_by('-created_at')
    
    @action(detail=True, methods=['post'])
    def mark_paid(self, request, pk=None):
        """Mark a payslip as paid"""
        payslip = self.get_object()
        payslip.status = 'PAID'
        payslip.payment_date = timezone.now().date()
        payslip.save()
        return Response({'message': 'Payslip marked as paid'})
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get payroll summary for a given month"""
        month = request.query_params.get('month')
        if not month:
            month = timezone.now().strftime('%Y-%m')
        
        try:
            year, month_num = month.split('-')
            payslips = Payslip.objects.filter(
                payroll_period__start_date__year=year,
                payroll_period__start_date__month=month_num
            )
        except ValueError:
            payslips = Payslip.objects.none()
        
        summary = payslips.aggregate(
            total_basic=Sum('basic_salary'),
            total_allowances=Sum('total_allowances'),
            total_deductions=Sum('total_deductions'),
            total_net=Sum('net_salary'),
            total_count=Count('id')
        )
        
        processed = payslips.filter(status__in=['GENERATED', 'PAID']).count()
        pending = payslips.filter(status='PENDING').count()
        
        return Response({
            'month': month,
            'total_employees': summary['total_count'] or 0,
            'total_basic_salary': float(summary['total_basic'] or 0),
            'total_allowances': float(summary['total_allowances'] or 0),
            'total_deductions': float(summary['total_deductions'] or 0),
            'total_net_salary': float(summary['total_net'] or 0),
            'processed_count': processed,
            'pending_count': pending
        })


class AllowanceViewSet(viewsets.ModelViewSet):
    """ViewSet for Allowance CRUD operations"""
    queryset = Allowance.objects.all().select_related('employee')
    serializer_class = AllowanceSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        employee_id = self.request.query_params.get('employee_id')
        is_active = self.request.query_params.get('is_active')
        
        if employee_id:
            queryset = queryset.filter(employee_id=employee_id)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        return queryset.order_by('-created_at')


class BonusViewSet(viewsets.ModelViewSet):
    """ViewSet for Bonus CRUD operations"""
    queryset = Bonus.objects.all().select_related('employee', 'approved_by')
    serializer_class = BonusSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        employee_id = self.request.query_params.get('employee_id')
        status_filter = self.request.query_params.get('status')
        
        if employee_id:
            queryset = queryset.filter(employee_id=employee_id)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset.order_by('-created_at')
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve a bonus"""
        bonus = self.get_object()
        bonus.status = 'APPROVED'
        bonus.approved_by = request.user
        bonus.save()
        return Response({'message': 'Bonus approved'})
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Reject a bonus"""
        bonus = self.get_object()
        bonus.status = 'REJECTED'
        bonus.save()
        return Response({'message': 'Bonus rejected'})


class TaxBracketViewSet(viewsets.ModelViewSet):
    """ViewSet for TaxBracket CRUD operations"""
    queryset = TaxBracket.objects.all()
    serializer_class = TaxBracketSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        is_active = self.request.query_params.get('is_active')
        
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        return queryset.order_by('min_income')


class ProcessPayrollView(APIView):
    """Process payroll for a given month"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = ProcessPayrollSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        month = serializer.validated_data['month']
        employee_ids = serializer.validated_data.get('employee_ids', [])
        
        try:
            year, month_num = month.split('-')
            year = int(year)
            month_num = int(month_num)
        except ValueError:
            return Response(
                {'error': 'Invalid month format. Use YYYY-MM'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get or create payroll period
        start_date = datetime(year, month_num, 1).date()
        if month_num == 12:
            end_date = datetime(year + 1, 1, 1).date()
        else:
            end_date = datetime(year, month_num + 1, 1).date()
        
        from datetime import timedelta
        end_date = end_date - timedelta(days=1)
        
        period, created = PayrollPeriod.objects.get_or_create(
            start_date=start_date,
            end_date=end_date,
            defaults={
                'name': f"Payroll {start_date.strftime('%B %Y')}",
                'payment_date': end_date,
                'status': 'PROCESSING'
            }
        )
        
        # Get employees to process
        if employee_ids:
            employees = Employee.objects.filter(
                id__in=employee_ids,
                employment_status='ACTIVE'
            )
        else:
            employees = Employee.objects.filter(employment_status='ACTIVE')
        
        processed = []
        errors = []
        
        for employee in employees:
            try:
                # Check if payslip already exists
                existing = Payslip.objects.filter(
                    employee=employee,
                    payroll_period=period
                ).first()
                
                if existing:
                    processed.append({
                        'employee_id': employee.id,
                        'employee_name': f"{employee.first_name} {employee.last_name}",
                        'status': 'already_exists',
                        'payslip_id': existing.id
                    })
                    continue
                
                # Calculate salary components
                basic_salary = getattr(employee, 'base_salary', None) or Decimal('50000.00')
                
                # Get active allowances for this employee
                allowances = Allowance.objects.filter(
                    employee=employee,
                    is_active=True
                ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
                
                # Get approved bonuses for this month
                bonuses = Bonus.objects.filter(
                    employee=employee,
                    status='APPROVED',
                    payment_date__year=year,
                    payment_date__month=month_num
                ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
                
                # Calculate gross salary
                gross_salary = basic_salary + allowances + bonuses
                
                # Calculate deductions (simplified - 15% tax + other deductions)
                tax_rate = Decimal('0.15')
                tax_amount = gross_salary * tax_rate
                other_deductions = Decimal('0')  # Can be expanded
                total_deductions = tax_amount + other_deductions
                
                # Calculate net salary
                net_salary = gross_salary - total_deductions
                
                # Create payslip
                payslip = Payslip.objects.create(
                    employee=employee,
                    payroll_period=period,
                    basic_salary=basic_salary,
                    gross_salary=gross_salary,
                    total_allowances=allowances,
                    total_bonuses=bonuses,
                    tax_amount=tax_amount,
                    total_deductions=total_deductions,
                    net_salary=net_salary,
                    status='GENERATED'
                )
                
                # Create earning records
                PayslipEarning.objects.create(
                    payslip=payslip,
                    earning_type='BASIC',
                    description='Basic Salary',
                    amount=basic_salary
                )
                
                if allowances > 0:
                    PayslipEarning.objects.create(
                        payslip=payslip,
                        earning_type='ALLOWANCE',
                        description='Total Allowances',
                        amount=allowances
                    )
                
                if bonuses > 0:
                    PayslipEarning.objects.create(
                        payslip=payslip,
                        earning_type='BONUS',
                        description='Total Bonuses',
                        amount=bonuses
                    )
                
                # Create deduction records
                PayslipDeduction.objects.create(
                    payslip=payslip,
                    deduction_type='TAX',
                    description='Income Tax',
                    amount=tax_amount
                )
                
                processed.append({
                    'employee_id': employee.id,
                    'employee_name': f"{employee.first_name} {employee.last_name}",
                    'status': 'success',
                    'payslip_id': payslip.id,
                    'net_salary': float(net_salary)
                })
                
            except Exception as e:
                errors.append({
                    'employee_id': employee.id,
                    'employee_name': f"{employee.first_name} {employee.last_name}",
                    'error': str(e)
                })
        
        # Update period status
        period.status = 'PROCESSED'
        period.save()
        
        return Response({
            'message': f'Payroll processed for {month}',
            'period_id': period.id,
            'processed_count': len([p for p in processed if p['status'] == 'success']),
            'already_exists_count': len([p for p in processed if p['status'] == 'already_exists']),
            'error_count': len(errors),
            'processed': processed,
            'errors': errors
        })


class GeneratePayslipsView(APIView):
    """Generate payslips for display (without saving to DB)"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        month = request.query_params.get('month')
        if not month:
            month = timezone.now().strftime('%Y-%m')
        
        try:
            year, month_num = month.split('-')
            year = int(year)
            month_num = int(month_num)
        except ValueError:
            return Response(
                {'error': 'Invalid month format. Use YYYY-MM'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if payroll period exists with payslips
        start_date = datetime(year, month_num, 1).date()
        if month_num == 12:
            end_date = datetime(year + 1, 1, 1).date()
        else:
            end_date = datetime(year, month_num + 1, 1).date()
        
        from datetime import timedelta
        end_date = end_date - timedelta(days=1)
        
        period = PayrollPeriod.objects.filter(
            start_date=start_date,
            end_date=end_date
        ).first()
        
        if period:
            # Return existing payslips
            payslips = Payslip.objects.filter(
                payroll_period=period
            ).select_related('employee', 'employee__department')
            
            serializer = PayslipSerializer(payslips, many=True)
            return Response({
                'month': month,
                'period_id': period.id,
                'period_status': period.status,
                'payslips': serializer.data,
                'source': 'database'
            })
        
        # Generate preview payslips (not saved)
        employees = Employee.objects.filter(
            employment_status='ACTIVE'
        ).select_related('department')
        
        preview_payslips = []
        
        for employee in employees:
            basic_salary = getattr(employee, 'base_salary', None) or Decimal('50000.00')
            
            # Get active allowances
            allowances = Allowance.objects.filter(
                employee=employee,
                is_active=True
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
            
            # Calculate
            gross_salary = basic_salary + allowances
            tax_amount = gross_salary * Decimal('0.15')
            total_deductions = tax_amount
            net_salary = gross_salary - total_deductions
            
            preview_payslips.append({
                'employee': employee.id,
                'employee_id': employee.employee_id,
                'employee_name': f"{employee.first_name} {employee.last_name}",
                'department_name': employee.department.name if employee.department else None,
                'basic_salary': float(basic_salary),
                'total_allowances': float(allowances),
                'gross_salary': float(gross_salary),
                'tax_amount': float(tax_amount),
                'total_deductions': float(total_deductions),
                'net_salary': float(net_salary),
                'status': 'PREVIEW'
            })
        
        # Calculate totals
        total_basic = sum(p['basic_salary'] for p in preview_payslips)
        total_allowances = sum(p['total_allowances'] for p in preview_payslips)
        total_deductions = sum(p['total_deductions'] for p in preview_payslips)
        total_net = sum(p['net_salary'] for p in preview_payslips)
        
        return Response({
            'month': month,
            'period_id': None,
            'period_status': 'NOT_PROCESSED',
            'payslips': preview_payslips,
            'source': 'preview',
            'summary': {
                'total_employees': len(preview_payslips),
                'total_basic_salary': total_basic,
                'total_allowances': total_allowances,
                'total_deductions': total_deductions,
                'total_net_salary': total_net
            }
        })
    
    def post(self, request):
        """Generate and save payslips"""
        # Redirect to ProcessPayrollView
        process_view = ProcessPayrollView()
        return process_view.post(request)


class PayrollStatsView(APIView):
    """Get overall payroll statistics"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        month = request.query_params.get('month')
        if not month:
            month = timezone.now().strftime('%Y-%m')
        
        try:
            year, month_num = month.split('-')
        except ValueError:
            return Response(
                {'error': 'Invalid month format'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get active employees
        active_employees = Employee.objects.filter(employment_status='ACTIVE').count()
        
        # Get payslips for the month
        payslips = Payslip.objects.filter(
            payroll_period__start_date__year=year,
            payroll_period__start_date__month=month_num
        )
        
        stats = payslips.aggregate(
            total_basic=Sum('basic_salary'),
            total_allowances=Sum('total_allowances'),
            total_deductions=Sum('total_deductions'),
            total_net=Sum('net_salary'),
            count=Count('id')
        )
        
        return Response({
            'month': month,
            'active_employees': active_employees,
            'processed_employees': stats['count'] or 0,
            'total_basic_salary': float(stats['total_basic'] or 0),
            'total_allowances': float(stats['total_allowances'] or 0),
            'total_deductions': float(stats['total_deductions'] or 0),
            'total_net_salary': float(stats['total_net'] or 0),
        })
