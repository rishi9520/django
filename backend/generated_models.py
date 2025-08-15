# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Admins(models.Model):
    school_id = models.CharField(max_length=50, blank=True, null=True)
    username = models.CharField(max_length=255, blank=True, null=True)
    password = models.CharField(max_length=255, blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    teacher_id = models.CharField(max_length=50, blank=True, null=True)
    email = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'admins'
        unique_together = (('school_id', 'username'),)


class Arrangements(models.Model):
    school_id = models.CharField(max_length=50, blank=True, null=True)
    date = models.DateField(blank=True, null=True)
    absent_teacher = models.CharField(max_length=50, blank=True, null=True)
    absent_name = models.CharField(max_length=255, blank=True, null=True)
    absent_category = models.CharField(max_length=50, blank=True, null=True)
    replacement_teacher = models.CharField(max_length=50, blank=True, null=True)
    replacement_name = models.CharField(max_length=255, blank=True, null=True)
    replacement_category = models.CharField(max_length=50, blank=True, null=True)
    class_field = models.CharField(db_column='class', max_length=50, blank=True, null=True)  # Field renamed because it was a Python reserved word.
    period = models.IntegerField(blank=True, null=True)
    status = models.CharField(max_length=50, blank=True, null=True)
    match_quality = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'arrangements'


class Attendance(models.Model):
    school_id = models.CharField(max_length=50, blank=True, null=True)
    date = models.DateField(blank=True, null=True)
    teacher_id = models.CharField(max_length=50, blank=True, null=True)
    status = models.CharField(max_length=20, blank=True, null=True)
    timestamp = models.DateTimeField(blank=True, null=True)
    is_auto = models.IntegerField(blank=True, null=True)
    biometric_code = models.CharField(unique=True, max_length=25, blank=True, null=True)
    marked_by = models.CharField(max_length=50, blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'attendance'
        unique_together = (('school_id', 'teacher_id', 'date'),)


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=80)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=50)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField()
    is_superuser = models.IntegerField()
    username = models.CharField(unique=True, max_length=30)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.CharField(max_length=75)
    is_staff = models.IntegerField()
    is_active = models.IntegerField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class BillingPlans(models.Model):
    plan_name = models.CharField(max_length=50)
    monthly_price = models.DecimalField(max_digits=10, decimal_places=2)
    yearly_price = models.DecimalField(max_digits=10, decimal_places=2)
    features = models.JSONField(blank=True, null=True)
    is_premium = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'billing_plans'


class DailySchedules(models.Model):
    school_id = models.CharField(max_length=50, blank=True, null=True)
    day_of_week = models.CharField(max_length=20, blank=True, null=True)
    teacher_id = models.CharField(max_length=50, blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    category = models.CharField(max_length=50, blank=True, null=True)
    subject = models.CharField(max_length=255, blank=True, null=True)
    period_number = models.IntegerField(blank=True, null=True)
    class_info = models.CharField(max_length=255, blank=True, null=True)
    classes = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'daily_schedules'


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.PositiveSmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    name = models.CharField(max_length=100)
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    id = models.BigAutoField(primary_key=True)
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class PaymentMethods(models.Model):
    method_id = models.AutoField(primary_key=True)
    method_type = models.CharField(max_length=50)
    method_name = models.CharField(max_length=100)
    method_value = models.CharField(max_length=200)
    additional_info = models.JSONField(blank=True, null=True)
    is_active = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'payment_methods'


class SchoolLogic(models.Model):
    school_id = models.CharField(unique=True, max_length=50)
    logic_name = models.CharField(max_length=255, blank=True, null=True)
    logic_code = models.TextField()
    is_active = models.IntegerField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'school_logic'


class Schools(models.Model):
    school_id = models.CharField(primary_key=True, max_length=50)
    school_name = models.CharField(max_length=255, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    email = models.CharField(max_length=255, blank=True, null=True)
    api_key = models.CharField(unique=True, max_length=100, blank=True, null=True)
    logourl = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'schools'


class SuspendedDates(models.Model):
    school_id = models.CharField(max_length=50, blank=True, null=True)
    date = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'suspended_dates'


class Timing(models.Model):
    timing_id = models.AutoField(primary_key=True)
    school_id = models.CharField(unique=True, max_length=50)
    hour = models.IntegerField()
    minute = models.IntegerField()
    enabled = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'timing'


class Users(models.Model):
    school_id = models.CharField(max_length=50, blank=True, null=True)
    teacher_id = models.CharField(max_length=50, blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    category = models.CharField(max_length=50, blank=True, null=True)
    biometric_code = models.CharField(unique=True, max_length=25, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'users'


class WorkloadCounter(models.Model):
    school_id = models.CharField(max_length=50, blank=True, null=True)
    teacher_id = models.CharField(max_length=50, blank=True, null=True)
    workload_count = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'workload_counter'
