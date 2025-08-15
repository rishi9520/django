
from rest_framework import serializers
from .models import School, Admin

class SchoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = School
        fields = ['school_id', 'school_name', 'address', 'email', 'logourl']

class AdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Admin
        fields = ['id', 'school_id', 'username', 'name', 'phone', 'teacher_id', 'email']
        extra_kwargs = {'password': {'write_only': True}}
