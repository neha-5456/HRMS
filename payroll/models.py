from django.db import models
from django.conf import settings


class PayrollPeriod(models.Model):
    """Payroll processing periods"""
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('PROCESSING', 'Processing'),
        ('PROCESSED', 'Processed'),
        ('CLOSED', 'Closed'),
    ]
    
    name = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    payment_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-start_date']
    
    def __str__(self):
        return f"{self.name} ({self.start_date} to {self.end_date})"


class Payslip(models.Model):
    """Employee payslips"""
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('GENERATED', 'Generated'),
        ('PAID', 'Paid'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('BANK_TRANSFER', 'Bank Transfer'),
        ('CHECK', 'Check'),
        ('CASH', 'Cash'),
    ]
    
    employee = models.ForeignKey(
        'employees.Employee',
        on_delete=models.CASCADE,
        related_name='payslips'
    )
    payroll_period = models.ForeignKey(
        PayrollPeriod,
        on_delete=models.CASCADE,
        related_name='payslips'
    )
    basic_salary = models.DecimalField(max_digits=12, decimal_places=2)
    gross_salary = models.DecimalField(max_digits=12, decimal_places=2)
    total_deductions = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    net_salary = models.DecimalField(max_digits=12, decimal_places=2)
    total_allowances = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_bonuses = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    payment_date = models.DateField(null=True, blank=True)
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        default='BANK_TRANSFER'
    )
    bank_account = models.CharField(max_length=50, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['employee', 'payroll_period']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.employee} - {self.payroll_period}"


class PayslipEarning(models.Model):
    """Earnings breakdown for payslip"""
    EARNING_TYPE_CHOICES = [
        ('BASIC', 'Basic Salary'),
        ('ALLOWANCE', 'Allowance'),
        ('BONUS', 'Bonus'),
        ('OVERTIME', 'Overtime'),
        ('OTHER', 'Other'),
    ]
    
    payslip = models.ForeignKey(
        Payslip,
        on_delete=models.CASCADE,
        related_name='earnings'
    )
    earning_type = models.CharField(max_length=20, choices=EARNING_TYPE_CHOICES)
    description = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    
    def __str__(self):
        return f"{self.payslip} - {self.description}: {self.amount}"


class PayslipDeduction(models.Model):
    """Deductions breakdown for payslip"""
    DEDUCTION_TYPE_CHOICES = [
        ('TAX', 'Income Tax'),
        ('INSURANCE', 'Insurance'),
        ('PF', 'Provident Fund'),
        ('LOAN', 'Loan Repayment'),
        ('OTHER', 'Other'),
    ]
    
    payslip = models.ForeignKey(
        Payslip,
        on_delete=models.CASCADE,
        related_name='deductions'
    )
    deduction_type = models.CharField(max_length=20, choices=DEDUCTION_TYPE_CHOICES)
    description = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    
    def __str__(self):
        return f"{self.payslip} - {self.description}: {self.amount}"


class Allowance(models.Model):
    """Employee allowances"""
    ALLOWANCE_TYPE_CHOICES = [
        ('HRA', 'House Rent Allowance'),
        ('TA', 'Travel Allowance'),
        ('DA', 'Dearness Allowance'),
        ('MEDICAL', 'Medical Allowance'),
        ('SPECIAL', 'Special Allowance'),
        ('OTHER', 'Other'),
    ]
    
    employee = models.ForeignKey(
        'employees.Employee',
        on_delete=models.CASCADE,
        related_name='allowances'
    )
    allowance_type = models.CharField(max_length=20, choices=ALLOWANCE_TYPE_CHOICES)
    name = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    is_taxable = models.BooleanField(default=True)
    is_recurring = models.BooleanField(default=True)
    effective_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.employee} - {self.name}: {self.amount}"


class Bonus(models.Model):
    """Employee bonuses"""
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('PAID', 'Paid'),
    ]
    
    BONUS_TYPE_CHOICES = [
        ('PERFORMANCE', 'Performance Bonus'),
        ('ANNUAL', 'Annual Bonus'),
        ('FESTIVAL', 'Festival Bonus'),
        ('PROJECT', 'Project Bonus'),
        ('REFERRAL', 'Referral Bonus'),
        ('OTHER', 'Other'),
    ]
    
    employee = models.ForeignKey(
        'employees.Employee',
        on_delete=models.CASCADE,
        related_name='bonuses'
    )
    bonus_type = models.CharField(max_length=20, choices=BONUS_TYPE_CHOICES)
    name = models.CharField(max_length=255, default="bonus")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    is_taxable = models.BooleanField(default=True)
    payment_date = models.DateField(null=True, blank=True)
    reason = models.TextField(blank=True)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_bonuses'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.employee} - {self.name}: {self.amount}"


class TaxBracket(models.Model):
    """Tax brackets for salary calculations"""
    name = models.CharField(max_length=100)
    min_income = models.DecimalField(max_digits=12, decimal_places=2)
    max_income = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2)  # Percentage
    fixed_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    effective_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['min_income']
    
    def __str__(self):
        return f"{self.name}: {self.tax_rate}%"
