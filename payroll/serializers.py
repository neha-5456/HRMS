from rest_framework import serializers
from .models import (
    PayrollPeriod, Payslip, PayslipEarning, PayslipDeduction,
    Allowance, Bonus, TaxBracket
)
from employees.models import Employee


class PayslipEarningSerializer(serializers.ModelSerializer):
    class Meta:
        model = PayslipEarning
        fields = ['id', 'earning_type', 'description', 'amount']


class PayslipDeductionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PayslipDeduction
        fields = ['id', 'deduction_type', 'description', 'amount']


class PayslipSerializer(serializers.ModelSerializer):
    employee_name = serializers.SerializerMethodField()
    employee_id = serializers.SerializerMethodField()
    department_name = serializers.SerializerMethodField()
    earnings = PayslipEarningSerializer(many=True, read_only=True)
    deductions = PayslipDeductionSerializer(many=True, read_only=True)
    
    class Meta:
        model = Payslip
        fields = [
            'id', 'employee', 'employee_name', 'employee_id', 'department_name',
            'payroll_period', 'basic_salary', 'gross_salary', 'total_deductions',
            'net_salary', 'total_allowances', 'total_bonuses', 'tax_amount',
            'status', 'payment_date', 'payment_method', 'bank_account',
            'notes', 'earnings', 'deductions', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_employee_name(self, obj):
        return f"{obj.employee.first_name} {obj.employee.last_name}"
    
    def get_employee_id(self, obj):
        return obj.employee.employee_id
    
    def get_department_name(self, obj):
        if obj.employee.department:
            return obj.employee.department.name
        return None


class PayslipCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payslip
        fields = [
            'employee', 'payroll_period', 'basic_salary', 'gross_salary',
            'total_deductions', 'net_salary', 'total_allowances', 'total_bonuses',
            'tax_amount', 'status', 'payment_date', 'payment_method',
            'bank_account', 'notes'
        ]


class PayrollPeriodSerializer(serializers.ModelSerializer):
    payslip_count = serializers.SerializerMethodField()
    total_net_salary = serializers.SerializerMethodField()
    
    class Meta:
        model = PayrollPeriod
        fields = [
            'id', 'name', 'start_date', 'end_date', 'payment_date',
            'status', 'payslip_count', 'total_net_salary', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_payslip_count(self, obj):
        return obj.payslips.count()
    
    def get_total_net_salary(self, obj):
        total = sum(p.net_salary for p in obj.payslips.all())
        return float(total)


class AllowanceSerializer(serializers.ModelSerializer):
    employee_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Allowance
        fields = [
            'id', 'employee', 'employee_name', 'allowance_type', 'name',
            'amount', 'is_taxable', 'is_recurring', 'effective_date',
            'end_date', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_employee_name(self, obj):
        return f"{obj.employee.first_name} {obj.employee.last_name}"


class BonusSerializer(serializers.ModelSerializer):
    employee_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Bonus
        fields = [
            'id', 'employee', 'employee_name', 'bonus_type', 'name',
            'amount', 'is_taxable', 'payment_date', 'reason',
            'approved_by', 'status', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_employee_name(self, obj):
        return f"{obj.employee.first_name} {obj.employee.last_name}"


class TaxBracketSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaxBracket
        fields = [
            'id', 'name', 'min_income', 'max_income', 'tax_rate',
            'fixed_amount', 'is_active', 'effective_date', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class ProcessPayrollSerializer(serializers.Serializer):
    """Serializer for processing payroll"""
    month = serializers.CharField(required=True, help_text="Month in YYYY-MM format")
    employee_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        help_text="List of employee IDs to process. If empty, process all active employees."
    )


class GeneratePayslipSerializer(serializers.Serializer):
    """Serializer for generating individual payslip"""
    employee_id = serializers.IntegerField(required=True)
    month = serializers.CharField(required=True, help_text="Month in YYYY-MM format")
    basic_salary = serializers.DecimalField(max_digits=12, decimal_places=2, required=False)


class PayrollSummarySerializer(serializers.Serializer):
    """Serializer for payroll summary response"""
    month = serializers.CharField()
    total_employees = serializers.IntegerField()
    total_basic_salary = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_allowances = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_deductions = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_net_salary = serializers.DecimalField(max_digits=15, decimal_places=2)
    processed_count = serializers.IntegerField()
    pending_count = serializers.IntegerField()
