from django.db import models
from django.conf import settings


class Attendance(models.Model):
    """Employee attendance records"""
    STATUS_CHOICES = [
        ('PRESENT', 'Present'),
        ('ABSENT', 'Absent'),
        ('LATE', 'Late'),
        ('HALF_DAY', 'Half Day'),
        ('ON_LEAVE', 'On Leave'),
    ]
    
    employee = models.ForeignKey(
        'employees.Employee',
        on_delete=models.CASCADE,
        related_name='attendance_records'
    )
    date = models.DateField()
    check_in_time = models.TimeField(null=True, blank=True)
    check_out_time = models.TimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PRESENT')
    work_hours = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    overtime_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    is_remote = models.BooleanField(default=False)
    location = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['employee', 'date']
        ordering = ['-date', 'employee__user__first_name']
    
    def __str__(self):
        return f"{self.employee} - {self.date} - {self.status}"


class Holiday(models.Model):
    """Company holidays"""
    HOLIDAY_TYPE_CHOICES = [
        ('PUBLIC', 'Public Holiday'),
        ('COMPANY', 'Company Holiday'),
        ('OPTIONAL', 'Optional Holiday'),
    ]
    
    name = models.CharField(max_length=100)
    date = models.DateField()
    description = models.TextField(blank=True)
    is_recurring = models.BooleanField(default=False)
    holiday_type = models.CharField(max_length=20, choices=HOLIDAY_TYPE_CHOICES, default='PUBLIC')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['date']
    
    def __str__(self):
        return f"{self.name} - {self.date}"


class WorkSchedule(models.Model):
    """Work schedule for employees"""
    DAY_CHOICES = [
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    ]
    
    employee = models.ForeignKey(
        'employees.Employee',
        on_delete=models.CASCADE,
        related_name='work_schedules',
        null=True,
        blank=True
    )
    day_of_week = models.IntegerField(choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_working_day = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['employee', 'day_of_week']
    
    def __str__(self):
        day_name = dict(self.DAY_CHOICES).get(self.day_of_week)
        return f"{self.employee or 'Default'} - {day_name}"
