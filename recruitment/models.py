# Create your models here.
from django.db import models
from departments.models import Department, Position
from employees.models import Employee

class JobPosting(models.Model):
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('OPEN', 'Open'),
        ('CLOSED', 'Closed'),
        ('ON_HOLD', 'On Hold'),
    ]
    
    JOB_TYPE_CHOICES = [
        ('FULL_TIME', 'Full Time'),
        ('PART_TIME', 'Part Time'),
        ('CONTRACT', 'Contract'),
        ('INTERN', 'Intern'),
    ]
    
    title = models.CharField(max_length=200)
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name='job_postings'
    )
    position = models.ForeignKey(
        Position,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='job_postings'
    )
    job_type = models.CharField(max_length=20, choices=JOB_TYPE_CHOICES)
    description = models.TextField()
    requirements = models.TextField()
    responsibilities = models.TextField()
    
    min_salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    max_salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=3, default='USD')
    
    location = models.CharField(max_length=200)
    number_of_openings = models.IntegerField(default=1)
    
    posted_date = models.DateField(auto_now_add=True)
    closing_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    
    created_by = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_job_postings'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title
    
    class Meta:
        db_table = 'job_postings'
        ordering = ['-posted_date']

class Candidate(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    
    current_company = models.CharField(max_length=200, blank=True)
    current_position = models.CharField(max_length=100, blank=True)
    total_experience_years = models.IntegerField(default=0)
    
    resume = models.FileField(upload_to='candidate_resumes/')
    cover_letter = models.TextField(blank=True)
    portfolio_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    class Meta:
        db_table = 'candidates'
        ordering = ['-created_at']

class Application(models.Model):
    STATUS_CHOICES = [
        ('APPLIED', 'Applied'),
        ('SCREENING', 'Screening'),
        ('SHORTLISTED', 'Shortlisted'),
        ('INTERVIEW_SCHEDULED', 'Interview Scheduled'),
        ('INTERVIEWED', 'Interviewed'),
        ('OFFERED', 'Offered'),
        ('HIRED', 'Hired'),
        ('REJECTED', 'Rejected'),
        ('WITHDRAWN', 'Withdrawn'),
    ]
    
    job_posting = models.ForeignKey(
        JobPosting,
        on_delete=models.CASCADE,
        related_name='applications'
    )
    candidate = models.ForeignKey(
        Candidate,
        on_delete=models.CASCADE,
        related_name='applications'
    )
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='APPLIED')
    
    expected_salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    available_from = models.DateField(null=True, blank=True)
    
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.candidate} - {self.job_posting.title}"
    
    class Meta:
        db_table = 'applications'
        unique_together = ['job_posting', 'candidate']
        ordering = ['-created_at']

class Interview(models.Model):
    INTERVIEW_TYPE_CHOICES = [
        ('PHONE', 'Phone Screen'),
        ('VIDEO', 'Video Interview'),
        ('IN_PERSON', 'In Person'),
        ('TECHNICAL', 'Technical Round'),
        ('HR', 'HR Round'),
        ('FINAL', 'Final Round'),
    ]
    
    STATUS_CHOICES = [
        ('SCHEDULED', 'Scheduled'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
        ('RESCHEDULED', 'Rescheduled'),
    ]
    
    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name='interviews'
    )
    interview_type = models.CharField(max_length=20, choices=INTERVIEW_TYPE_CHOICES)
    scheduled_date = models.DateField()
    scheduled_time = models.TimeField()
    duration_minutes = models.IntegerField(default=60)
    
    interviewer = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        related_name='conducted_interviews'
    )
    
    location = models.CharField(max_length=200, blank=True)
    meeting_link = models.URLField(blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='SCHEDULED')
    
    feedback = models.TextField(blank=True)
    rating = models.IntegerField(null=True, blank=True)
    recommendation = models.CharField(
        max_length=20,
        choices=[
            ('HIRE', 'Hire'),
            ('MAYBE', 'Maybe'),
            ('NO_HIRE', 'No Hire'),
        ],
        blank=True
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'interviews'
        ordering = ['scheduled_date', 'scheduled_time']

class Offer(models.Model):
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('SENT', 'Sent'),
        ('ACCEPTED', 'Accepted'),
        ('REJECTED', 'Rejected'),
        ('EXPIRED', 'Expired'),
    ]
    
    application = models.OneToOneField(
        Application,
        on_delete=models.CASCADE,
        related_name='offer'
    )
    
    position = models.CharField(max_length=100)
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE
    )
    
    offered_salary = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    
    start_date = models.DateField()
    employment_type = models.CharField(
        max_length=20,
        choices=[
            ('FULL_TIME', 'Full Time'),
            ('PART_TIME', 'Part Time'),
            ('CONTRACT', 'Contract'),
        ]
    )
    
    offer_letter = models.FileField(upload_to='offer_letters/', blank=True, null=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    sent_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    response_date = models.DateField(null=True, blank=True)
    
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'offers'
        ordering = ['-created_at']