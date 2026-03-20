# Create your models here.from django.db import models
from django.db import models
from employees.models import Employee

class LeaveType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    default_days_per_year = models.IntegerField()
    is_paid = models.BooleanField(default=True)
    requires_approval = models.BooleanField(default=True)
    max_consecutive_days = models.IntegerField(null=True, blank=True)
    color_code = models.CharField(max_length=7, default='#3498db')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        db_table = 'leave_types'
        ordering = ['name']

class LeaveBalance(models.Model):
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='leave_balances'
    )
    leave_type = models.ForeignKey(
        LeaveType,
        on_delete=models.CASCADE,
        related_name='balances'
    )
    year = models.IntegerField()
    total_days = models.DecimalField(max_digits=5, decimal_places=2)
    used_days = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    remaining_days = models.DecimalField(max_digits=5, decimal_places=2)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def calculate_remaining(self):
        self.remaining_days = self.total_days - self.used_days
    
    def save(self, *args, **kwargs):
        self.calculate_remaining()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.employee.employee_id} - {self.leave_type.name} ({self.year})"
    
    class Meta:
        db_table = 'leave_balances'
        unique_together = ['employee', 'leave_type', 'year']
        ordering = ['-year']

class LeaveRequest(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='leave_requests'
    )
    leave_type = models.ForeignKey(
        LeaveType,
        on_delete=models.CASCADE,
        related_name='requests'
    )
    start_date = models.DateField()
    end_date = models.DateField()
    total_days = models.DecimalField(max_digits=5, decimal_places=2)
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    
    approved_by = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_leave_requests'
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.employee.employee_id} - {self.leave_type.name} ({self.start_date} to {self.end_date})"
    
    class Meta:
        db_table = 'leave_requests'
        ordering = ['-created_at']

class LeaveApprovalWorkflow(models.Model):
    leave_request = models.ForeignKey(
        LeaveRequest,
        on_delete=models.CASCADE,
        related_name='approval_workflow'
    )
    approver = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='leave_approvals'
    )
    sequence = models.IntegerField()
    status = models.CharField(
        max_length=20,
        choices=LeaveRequest.STATUS_CHOICES,
        default='PENDING'
    )
    comments = models.TextField(blank=True)
    action_date = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'leave_approval_workflow'
        unique_together = ['leave_request', 'sequence']
        ordering = ['sequence']
