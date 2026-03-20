from django.db import models


class Department(models.Model):
    """Department model matching existing database"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    manager_id = models.BigIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'departments'
        managed = False
    
    def __str__(self):
        return self.name


class Position(models.Model):
    """Position model matching existing database"""
    title = models.CharField(max_length=100)
    description = models.TextField()
    level = models.CharField(max_length=50)
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name='positions',
        db_column='department_id'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'positions'
        managed = False
    
    def __str__(self):
        return self.title
