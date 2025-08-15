from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.db.models import Q
import sys
import os

# Add existing_modules to path to import preserved Python logic
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'existing_modules'))

from .models import User, DailySchedule, SchedulesSummary, WorkloadCounter, Substitute
from .serializers import UserSerializer, DailyScheduleSerializer, SchedulesSummarySerializer, WorkloadCounterSerializer, SubstituteSerializer
from authentication.models import School

# Import preserved logic
try:
    import data_manager
    from csv_importer import CSVImporter
except ImportError as e:
    print(f"Warning: Could not import preserved logic: {e}")
    data_manager = None
    CSVImporter = None

@api_view(['GET'])
@permission_classes([AllowAny])  # For development - should be authenticated
def get_teachers(request):
    """Get all teachers for a school"""
    school_id = request.GET.get('school_id')
    
    if not school_id:
        return Response({
            'success': False,
            'error': 'School ID is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        teachers = User.objects.filter(school_id=school_id)
        serializer = UserSerializer(teachers, many=True)
        return Response({
            'success': True,
            'teachers': serializer.data
        })
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
def add_teacher(request):
    """Add a new teacher"""
    try:
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'success': True,
                'message': 'Teacher added successfully',
                'teacher': serializer.data
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                'success': False,
                'error': 'Invalid data',
                'details': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PUT'])
@permission_classes([AllowAny])
def update_teacher(request, teacher_id):
    """Update teacher information"""
    try:
        teacher = User.objects.get(id=teacher_id)
        serializer = UserSerializer(teacher, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'success': True,
                'message': 'Teacher updated successfully',
                'teacher': serializer.data
            })
        else:
            return Response({
                'success': False,
                'error': 'Invalid data',
                'details': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
    except User.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Teacher not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['DELETE'])
@permission_classes([AllowAny])
def delete_teacher(request, teacher_id):
    """Delete a teacher"""
    try:
        teacher = User.objects.get(id=teacher_id)
        teacher.delete()
        return Response({
            'success': True,
            'message': 'Teacher deleted successfully'
        })
    except User.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Teacher not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_schedule(request):
    """Get schedule for a school"""
    school_id = request.GET.get('school_id')
    day_of_week = request.GET.get('day_of_week')
    
    if not school_id:
        return Response({
            'success': False,
            'error': 'School ID is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        schedules = DailySchedule.objects.filter(school_id=school_id)
        if day_of_week:
            schedules = schedules.filter(day_of_week=day_of_week)
            
        serializer = DailyScheduleSerializer(schedules, many=True)
        return Response({
            'success': True,
            'schedules': serializer.data
        })
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_workload(request):
    """Get workload counter for teachers"""
    school_id = request.GET.get('school_id')
    
    if not school_id:
        return Response({
            'success': False,
            'error': 'School ID is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        workloads = WorkloadCounter.objects.filter(school_id=school_id)
        serializer = WorkloadCounterSerializer(workloads, many=True)
        return Response({
            'success': True,
            'workloads': serializer.data
        })
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_substitutes(request):
    """Get substitute teachers for a school"""
    school_id = request.GET.get('school_id')
    
    if not school_id:
        return Response({
            'success': False,
            'error': 'School ID is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        substitutes = Substitute.objects.filter(school_id=school_id)
        serializer = SubstituteSerializer(substitutes, many=True)
        return Response({
            'success': True,
            'substitutes': serializer.data
        })
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)