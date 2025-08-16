from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.db import connection
from datetime import datetime, date

@api_view(['GET'])
@permission_classes([AllowAny])
def get_school_schedule(request, school_id):
    """Get complete school schedule"""
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    id, day_of_week, period, start_time, end_time,
                    class_name, section, subject, teacher_id
                FROM schedules 
                WHERE school_id = %s 
                ORDER BY day_of_week, period
            """, [school_id])
            
            schedule_data = []
            for row in cursor.fetchall():
                schedule_data.append({
                    'id': row[0],
                    'day_of_week': row[1],
                    'period': row[2],
                    'start_time': row[3],
                    'end_time': row[4],
                    'class_name': row[5],
                    'section': row[6],
                    'subject': row[7],
                    'teacher_id': row[8]
                })
            
            return Response({'schedule': schedule_data}, status=status.HTTP_200_OK)
    except Exception as e:
        print(f"Error fetching schedule: {e}")
        return Response(
            {'error': 'Failed to fetch schedule'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([AllowAny])
def get_teacher_schedule(request, school_id, teacher_id):
    """Get schedule for a specific teacher"""
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    day_of_week, period, start_time, end_time,
                    class_name, section, subject
                FROM schedules 
                WHERE school_id = %s AND teacher_id = %s
                ORDER BY day_of_week, period
            """, [school_id, teacher_id])
            
            teacher_schedule = []
            for row in cursor.fetchall():
                teacher_schedule.append({
                    'day_of_week': row[0],
                    'period': row[1],
                    'start_time': row[2],
                    'end_time': row[3],
                    'class_name': row[4],
                    'section': row[5],
                    'subject': row[6]
                })
            
            return Response({'teacher_schedule': teacher_schedule}, status=status.HTTP_200_OK)
    except Exception as e:
        print(f"Error fetching teacher schedule: {e}")
        return Response(
            {'error': 'Failed to fetch teacher schedule'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )