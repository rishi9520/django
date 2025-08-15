
from django.db import models

class School(models.Model):
    school_id = models.CharField(max_length=10, primary_key=True)
    school_name = models.CharField(max_length=255)
    address = models.TextField(blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    api_key = models.CharField(max_length=255, blank=True, null=True)
    logourl = models.URLField(blank=True, null=True)

    class Meta:
        db_table = 'schools'
        managed = False  # Django won't manage this table

    def __str__(self):
        return self.school_name

class Admin(models.Model):
    id = models.AutoField(primary_key=True)
    school_id = models.CharField(max_length=10, db_column='school_id')
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20, blank=True, null=True)
    teacher_id = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)

    class Meta:
        db_table = 'admins'
        managed = False  # Django won't manage this table

    def __str__(self):
        return f"{self.name} ({self.username})"
