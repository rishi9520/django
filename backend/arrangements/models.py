from django.db import models
from authentication.models import School

class Arrangement(models.Model):
    id = models.AutoField(primary_key=True)
    school = models.ForeignKey(School, on_delete=models.CASCADE, db_column='school_id')
    date = models.DateField()
    absent_teacher = models.CharField(max_length=255)
    replacement_teacher = models.CharField(max_length=255, blank=True, null=True)
    class_name = models.CharField(max_length=255, db_column='class')
    period = models.IntegerField()
    status = models.CharField(max_length=50, default='Pending')
    
    class Meta:
        db_table = 'arrangements'
    
    def __str__(self):
        return f"{self.absent_teacher} -> {self.replacement_teacher} ({self.date})"

class CoverageTracking(models.Model):
    id = models.AutoField(primary_key=True)
    school = models.ForeignKey(School, on_delete=models.CASCADE, db_column='school_id')
    date = models.DateField()
    period = models.IntegerField()
    class_name = models.CharField(max_length=255)
    section = models.CharField(max_length=50, blank=True, null=True)
    subject = models.CharField(max_length=255, blank=True, null=True)
    original_teacher_id = models.CharField(max_length=255)
    replacement_teacher_id = models.CharField(max_length=255, blank=True, null=True)
    
    class Meta:
        db_table = 'coverage_tracking'
    
    def __str__(self):
        return f"Coverage {self.date} P{self.period} - {self.class_name}"

class SuspendedDate(models.Model):
    id = models.AutoField(primary_key=True)
    school = models.ForeignKey(School, on_delete=models.CASCADE, db_column='school_id')
    date = models.DateField()
    
    class Meta:
        db_table = 'suspended_dates'
        unique_together = ('school', 'date')
    
    def __str__(self):
        return f"Suspended: {self.date}"

class SchoolLogic(models.Model):
    id = models.AutoField(primary_key=True)
    school = models.ForeignKey(School, on_delete=models.CASCADE, db_column='school_id')
    logic_name = models.CharField(max_length=255)
    logic_code = models.TextField()
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'school_logic'
        unique_together = ('school', 'logic_name')
    
    def __str__(self):
        return f"{self.logic_name} - {self.school.school_name}"
