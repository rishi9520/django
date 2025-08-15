from rest_framework import serializers
from .models import User, DailySchedule, SchedulesSummary, WorkloadCounter, Substitute
from authentication.models import School

class UserSerializer(serializers.ModelSerializer):
    school_name = serializers.CharField(source='school.school_name', read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'school', 'school_name', 'teacher_id', 'name', 'phone', 'category', 'biometric_code']

class DailyScheduleSerializer(serializers.ModelSerializer):
    school_name = serializers.CharField(source='school.school_name', read_only=True)
    
    class Meta:
        model = DailySchedule
        fields = ['id', 'school', 'school_name', 'day_of_week', 'teacher_id', 'name', 'category', 'subject', 'period_number', 'class_info']

class SchedulesSummarySerializer(serializers.ModelSerializer):
    school_name = serializers.CharField(source='school.school_name', read_only=True)
    
    class Meta:
        model = SchedulesSummary
        fields = ['id', 'school', 'school_name', 'teacher_id', 'name', 'category', 'subject', 
                 'period1', 'period2', 'period3', 'period4', 'period5', 'period6', 'period7']

class WorkloadCounterSerializer(serializers.ModelSerializer):
    school_name = serializers.CharField(source='school.school_name', read_only=True)
    
    class Meta:
        model = WorkloadCounter
        fields = ['id', 'school', 'school_name', 'teacher_id', 'workload_count']

class SubstituteSerializer(serializers.ModelSerializer):
    school_name = serializers.CharField(source='school.school_name', read_only=True)
    
    class Meta:
        model = Substitute
        fields = ['id', 'school', 'school_name', 'substitute_id', 'name', 'phone', 
                 'subject_expertise', 'qualification', 'availability', 'rating']