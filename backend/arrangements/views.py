from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.db import connection
from datetime import datetime, date

@api_view(['GET'])
@permission_classes([AllowAny])
def get_absent_teachers(request, school_id):
    """Get absent teachers for today"""
    try:
        today = request.GET.get('date', str(date.today()))
        
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT a.teacher_id, t.name 
                FROM attendance a
                JOIN teachers t ON a.teacher_id = t.teacher_id AND a.school_id = t.school_id
                WHERE a.school_id = %s 
                AND a.date = %s 
                AND a.status = 'absent'
            """, [school_id, today])
            
            absent_teachers = []
            for row in cursor.fetchall():
                absent_teachers.append({
                    'teacher_id': row[0],
                    'name': row[1]
                })
            
            return Response({'absent_teachers': absent_teachers}, status=status.HTTP_200_OK)
    except Exception as e:
        print(f"Error fetching absent teachers: {e}")
        return Response(
            {'error': 'Failed to fetch absent teachers'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([AllowAny])
def get_arrangements(request, school_id):
    """Get arrangements for a specific date"""
    try:
        today = request.GET.get('date', str(date.today()))
        
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    arr.id,
                    arr.absent_teacher_id,
                    arr.replacement_teacher_id,
                    arr.period,
                    arr.subject,
                    arr.class_name,
                    arr.section,
                    arr.match_quality,
                    t1.name as absent_teacher_name,
                    t2.name as replacement_teacher_name
                FROM arrangements arr
                LEFT JOIN teachers t1 ON arr.absent_teacher_id = t1.teacher_id AND arr.school_id = t1.school_id
                LEFT JOIN teachers t2 ON arr.replacement_teacher_id = t2.teacher_id AND arr.school_id = t2.school_id
                WHERE arr.school_id = %s AND arr.date = %s
                ORDER BY arr.period
            """, [school_id, today])
            
            arrangements = []
            for row in cursor.fetchall():
                arrangements.append({
                    'id': row[0],
                    'absent_teacher_id': row[1],
                    'replacement_teacher_id': row[2],
                    'period': row[3],
                    'subject': row[4],
                    'class_name': row[5],
                    'section': row[6],
                    'match_quality': row[7],
                    'absent_teacher_name': row[8],
                    'replacement_teacher_name': row[9]
                })
            
            return Response({'arrangements': arrangements}, status=status.HTTP_200_OK)
    except Exception as e:
        print(f"Error fetching arrangements: {e}")
        return Response(
            {'error': 'Failed to fetch arrangements'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([AllowAny])
def create_manual_arrangement(request, school_id):
    """Create a manual arrangement"""
    try:
        data = request.data
        absent_teacher_id = data.get('absent_teacher_id')
        replacement_teacher_id = data.get('replacement_teacher_id')
        period = data.get('period')
        subject = data.get('subject')
        class_name = data.get('class_name')
        section = data.get('section')
        arrangement_date = data.get('date', str(date.today()))
        
        if not all([absent_teacher_id, replacement_teacher_id, period, subject, class_name]):
            return Response(
                {'error': 'All fields are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO arrangements 
                (school_id, date, absent_teacher_id, replacement_teacher_id, period, subject, class_name, section, match_quality, type)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'manual', 'manual')
            """, [school_id, arrangement_date, absent_teacher_id, replacement_teacher_id, 
                  period, subject, class_name, section or ''])
            
            return Response(
                {'message': 'Manual arrangement created successfully'}, 
                status=status.HTTP_201_CREATED
            )
    except Exception as e:
        print(f"Error creating manual arrangement: {e}")
        return Response(
            {'error': 'Failed to create manual arrangement'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )