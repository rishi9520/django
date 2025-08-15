from django.db import models
from authentication.models import School

class User(models.Model):
    id = models.AutoField(primary_key=True)
    school = models.ForeignKey(School, on_delete=models.CASCADE, db_column='school_id')
    teacher_id = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20, blank=True, null=True)
    category = models.CharField(max_length=100, blank=True, null=True)
    biometric_code = models.CharField(max_length=255, blank=True, null=True)
    
    class Meta:
        db_table = 'users'
        unique_together = ('school', 'teacher_id')
    
    def __str__(self):
        return f"{self.name} ({self.teacher_id})"

class DailySchedule(models.Model):
    id = models.AutoField(primary_key=True)
    school = models.ForeignKey(School, on_delete=models.CASCADE, db_column='school_id')
    day_of_week = models.CharField(max_length=20)
    teacher_id = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=100, blank=True, null=True)
    subject = models.CharField(max_length=255, blank=True, null=True)
    period_number = models.IntegerField()
    class_info = models.CharField(max_length=255, blank=True, null=True)
    
    class Meta:
        db_table = 'daily_schedules'
    
    def __str__(self):
        return f"{self.name} - {self.day_of_week} Period {self.period_number}"

class SchedulesSummary(models.Model):
    id = models.AutoField(primary_key=True)
    school = models.ForeignKey(School, on_delete=models.CASCADE, db_column='school_id')
    teacher_id = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=100, blank=True, null=True)
    subject = models.CharField(max_length=255, blank=True, null=True)
    period1 = models.CharField(max_length=255, blank=True, null=True)
    period2 = models.CharField(max_length=255, blank=True, null=True)
    period3 = models.CharField(max_length=255, blank=True, null=True)
    period4 = models.CharField(max_length=255, blank=True, null=True)
    period5 = models.CharField(max_length=255, blank=True, null=True)
    period6 = models.CharField(max_length=255, blank=True, null=True)
    period7 = models.CharField(max_length=255, blank=True, null=True)
    
    class Meta:
        db_table = 'schedules_summary'
    
    def __str__(self):
        return f"{self.name} Schedule Summary"

class WorkloadCounter(models.Model):
    id = models.AutoField(primary_key=True)
    school = models.ForeignKey(School, on_delete=models.CASCADE, db_column='school_id')
    teacher_id = models.CharField(max_length=255)
    workload_count = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'workload_counter'
        unique_together = ('school', 'teacher_id')
    
    def __str__(self):
        return f"Teacher {self.teacher_id} - Workload: {self.workload_count}"

class Substitute(models.Model):
    id = models.AutoField(primary_key=True)
    school = models.ForeignKey(School, on_delete=models.CASCADE, db_column='school_id')
    substitute_id = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20, blank=True, null=True)
    subject_expertise = models.TextField(blank=True, null=True)
    qualification = models.CharField(max_length=255, blank=True, null=True)
    availability = models.CharField(max_length=100, default='Available')
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    
    class Meta:
        db_table = 'substitutes'
        unique_together = ('school', 'substitute_id')
    
    def __str__(self):
        return f"{self.name} (Substitute)"
