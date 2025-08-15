from django.db import models
from authentication.models import School

# Note: Schedule models are already defined in teachers/models.py
# This file can contain schedule-specific views or additional models if needed

class ScheduleTemplate(models.Model):
    """Template for creating schedules"""
    id = models.AutoField(primary_key=True)
    school_id = models.CharField(max_length=10, db_column='school_id')  # Match School.school_id field type
    template_name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'schedule_templates'
        managed = False  # Don't let Django manage this table structure
    
    def __str__(self):
        return f"{self.template_name} - {self.school.school_name}"
