from django.db import models
from django.conf import settings
from authentication.models import User

class Employee(models.Model):
    """Employee model matching EXACT database table structure"""
    
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    
    MARITAL_STATUS_CHOICES = [
        ('SINGLE', 'Single'),
        ('MARRIED', 'Married'),
        ('DIVORCED', 'Divorced'),
        ('WIDOWED', 'Widowed'),
    ]
    
    EMPLOYMENT_TYPE_CHOICES = [
        ('FULL_TIME', 'Full Time'),
        ('PART_TIME', 'Part Time'),
        ('CONTRACT', 'Contract'),
        ('INTERN', 'Intern'),
    ]
    
    # Foreign Keys
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='employee_profile',
        db_column='user_id'
    )
    department = models.ForeignKey(
        'departments.Department',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='employees',
        db_column='department_id'
    )
    position = models.ForeignKey(
        'departments.Position',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='employees',
        db_column='position_id'
    )
    manager = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='direct_reports',
        db_column='manager_id'
    )
    
    # Employee ID
    employee_id = models.CharField(max_length=20, unique=True)
    
    # Personal Information
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    marital_status = models.CharField(max_length=10, choices=MARITAL_STATUS_CHOICES)
    nationality = models.CharField(max_length=50)
    personal_email = models.EmailField()
    
    # Emergency Contact
    emergency_contact_name = models.CharField( null=True, max_length=100)
    emergency_contact_phone = models.CharField( null=True, max_length=15)
    emergency_contact_relation = models.CharField( null=True, max_length=50)
    
    # Address
    address_line1 = models.CharField( null=True, max_length=255)
    address_line2 = models.CharField( null=True, max_length=255, blank=True)
    city = models.CharField( null=True, max_length=100)
    state = models.CharField( null=True, max_length=100)
    postal_code = models.CharField( null=True, max_length=20)
    country = models.CharField( null=True, max_length=100)
    
    # Employment Details
    employment_type = models.CharField(max_length=20, choices=EMPLOYMENT_TYPE_CHOICES)
    date_of_joining = models.DateField()
    date_of_leaving = models.DateField(null=True, blank=True)
    probation_period_months = models.IntegerField(default=0)
    notice_period_days = models.IntegerField(default=0)
    
    # Salary
    basic_salary = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    
    # Documents
    resume = models.CharField(max_length=100, blank=True, null=True)
    id_document = models.CharField(max_length=100, blank=True, null=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'employees'
        managed = False
        ordering = ['employee_id']
    
    def __str__(self):
        try:
            return f"{self.employee_id} - {self.user.first_name} {self.user.last_name}"
        except:
            return self.employee_id
    
    @property
    def first_name(self):
        try:
            return self.user.first_name if self.user else ''
        except:
            return ''
    
    @property
    def last_name(self):
        try:
            return self.user.last_name if self.user else ''
        except:
            return ''
    
    @property
    def full_name(self):
        try:
            if self.user:
                return f"{self.user.first_name} {self.user.last_name}".strip()
        except:
            pass
        return self.employee_id
    
    @property
    def email(self):
        return self.personal_email
