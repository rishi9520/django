from django.db import models
from authentication.models import School

class Attendance(models.Model):
    id = models.AutoField(primary_key=True)
    school = models.ForeignKey(School, on_delete=models.CASCADE, db_column='school_id')
    date = models.DateField()
    teacher_id = models.CharField(max_length=255)
    status = models.CharField(max_length=50)  # Present, Absent, Late, etc.
    timestamp = models.DateTimeField()
    is_auto = models.BooleanField(default=False)  # Whether marked automatically
    biometric_code = models.CharField(max_length=255, blank=True, null=True)
    
    class Meta:
        db_table = 'attendance'
        unique_together = ('school', 'date', 'teacher_id')
    
    def __str__(self):
        return f"{self.teacher_id} - {self.date} ({self.status})"

class Timing(models.Model):
    timing_id = models.AutoField(primary_key=True)
    school = models.ForeignKey(School, on_delete=models.CASCADE, db_column='school_id')
    hour = models.IntegerField()
    minute = models.IntegerField()
    enabled = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'timing'
    
    def __str__(self):
        return f"{self.hour:02d}:{self.minute:02d} - {self.school.school_name}"
