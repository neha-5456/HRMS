from django.db import models
from employees.models import Employee

class PerformanceReviewCycle(models.Model):
    CYCLE_TYPE_CHOICES = [
        ('QUARTERLY', 'Quarterly'),
        ('SEMI_ANNUAL', 'Semi-Annual'),
        ('ANNUAL', 'Annual'),
    ]
    
    name = models.CharField(max_length=200)
    cycle_type = models.CharField(max_length=20, choices=CYCLE_TYPE_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField()
    review_deadline = models.DateField()
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        db_table = 'performance_review_cycles'
        ordering = ['-start_date']

class Goal(models.Model):
    STATUS_CHOICES = [
        ('NOT_STARTED', 'Not Started'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    PRIORITY_CHOICES = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('CRITICAL', 'Critical'),
    ]
    
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='goals'
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=100)
    
    start_date = models.DateField()
    target_date = models.DateField()
    completion_date = models.DateField(null=True, blank=True)
    
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='MEDIUM')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='NOT_STARTED')
    
    progress_percentage = models.IntegerField(default=0)
    
    created_by = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_goals'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.employee.employee_id} - {self.title}"
    
    class Meta:
        db_table = 'goals'
        ordering = ['-created_at']

class PerformanceReview(models.Model):
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('PENDING_EMPLOYEE', 'Pending Employee'),
        ('PENDING_MANAGER', 'Pending Manager'),
        ('COMPLETED', 'Completed'),
    ]
    
    RATING_CHOICES = [
        (1, 'Poor'),
        (2, 'Below Expectations'),
        (3, 'Meets Expectations'),
        (4, 'Exceeds Expectations'),
        (5, 'Outstanding'),
    ]
    
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='performance_reviews'
    )
    reviewer = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='conducted_reviews'
    )
    review_cycle = models.ForeignKey(
        PerformanceReviewCycle,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    
    # Self Assessment
    self_assessment = models.TextField(blank=True)
    self_rating = models.IntegerField(choices=RATING_CHOICES, null=True, blank=True)
    
    # Manager Assessment
    manager_feedback = models.TextField(blank=True)
    manager_rating = models.IntegerField(choices=RATING_CHOICES, null=True, blank=True)
    
    # Category Ratings
    technical_skills_rating = models.IntegerField(choices=RATING_CHOICES, null=True, blank=True)
    communication_rating = models.IntegerField(choices=RATING_CHOICES, null=True, blank=True)
    teamwork_rating = models.IntegerField(choices=RATING_CHOICES, null=True, blank=True)
    leadership_rating = models.IntegerField(choices=RATING_CHOICES, null=True, blank=True)
    problem_solving_rating = models.IntegerField(choices=RATING_CHOICES, null=True, blank=True)
    
    # Overall
    overall_rating = models.IntegerField(choices=RATING_CHOICES, null=True, blank=True)
    
    strengths = models.TextField(blank=True)
    areas_for_improvement = models.TextField(blank=True)
    development_plan = models.TextField(blank=True)
    
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='DRAFT')
    
    employee_acknowledgment = models.BooleanField(default=False)
    employee_acknowledgment_date = models.DateTimeField(null=True, blank=True)
    employee_comments = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.employee.employee_id} - {self.review_cycle.name}"
    
    class Meta:
        db_table = 'performance_reviews'
        unique_together = ['employee', 'review_cycle']
        ordering = ['-created_at']

class Feedback(models.Model):
    FEEDBACK_TYPE_CHOICES = [
        ('POSITIVE', 'Positive'),
        ('CONSTRUCTIVE', 'Constructive'),
        ('GENERAL', 'General'),
    ]
    
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='received_feedback'
    )
    given_by = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='given_feedback'
    )
    
    feedback_type = models.CharField(max_length=20, choices=FEEDBACK_TYPE_CHOICES)
    title = models.CharField(max_length=200)
    content = models.TextField()
    
    is_anonymous = models.BooleanField(default=False)
    is_shared_with_employee = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'feedback'
        ordering = ['-created_at']

class TrainingProgram(models.Model):
    STATUS_CHOICES = [
        ('PLANNED', 'Planned'),
        ('ONGOING', 'Ongoing'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField()
    instructor = models.CharField(max_length=200)
    
    start_date = models.DateField()
    end_date = models.DateField()
    duration_hours = models.IntegerField()
    
    max_participants = models.IntegerField()
    location = models.CharField(max_length=200)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PLANNED')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        db_table = 'training_programs'
        ordering = ['-start_date']

class TrainingEnrollment(models.Model):
    STATUS_CHOICES = [
        ('ENROLLED', 'Enrolled'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('DROPPED', 'Dropped'),
    ]
    
    training_program = models.ForeignKey(
        TrainingProgram,
        on_delete=models.CASCADE,
        related_name='enrollments'
    )
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='training_enrollments'
    )
    
    enrollment_date = models.DateField(auto_now_add=True)
    completion_date = models.DateField(null=True, blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ENROLLED')
    attendance_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    certificate = models.FileField(upload_to='certificates/', blank=True, null=True)
    
    feedback = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'training_enrollments'
        unique_together = ['training_program', 'employee']
        ordering = ['-enrollment_date']