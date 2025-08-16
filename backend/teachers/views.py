from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.db import connection
import json
from datetime import datetime

@api_view(['GET'])
@permission_classes([AllowAny])
def get_all_teachers(request, school_id):
    """Get all teachers for a school"""
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT teacher_id, name, phone, category, biometric_code 
                FROM teachers 
                WHERE school_id = %s 
                ORDER BY name
            """, [school_id])
            
            teachers_data = cursor.fetchall()
            teachers = []
            for teacher in teachers_data:
                teachers.append({
                    'teacher_id': teacher[0],
                    'name': teacher[1],
                    'phone': teacher[2],
                    'category': teacher[3],
                    'biometric_code': teacher[4] or ''
                })
            
            return Response({'teachers': teachers}, status=status.HTTP_200_OK)
    except Exception as e:
        print(f"Error fetching teachers: {e}")
        return Response(
            {'error': 'Failed to fetch teachers'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([AllowAny])
def add_teacher(request, school_id):
    """Add a new teacher"""
    try:
        data = request.data
        teacher_id = data.get('teacher_id')
        name = data.get('name')
        phone = data.get('phone')
        category = data.get('category')
        biometric_code = data.get('biometric_code', '')
        
        if not all([teacher_id, name, phone, category]):
            return Response(
                {'error': 'Teacher ID, name, phone and category are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        with connection.cursor() as cursor:
            # Check if teacher ID already exists
            cursor.execute(
                "SELECT COUNT(*) FROM teachers WHERE school_id = %s AND teacher_id = %s",
                [school_id, teacher_id]
            )
            if cursor.fetchone()[0] > 0:
                return Response(
                    {'error': 'Teacher ID already exists'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Insert new teacher
            cursor.execute("""
                INSERT INTO teachers (school_id, teacher_id, name, phone, category, biometric_code)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, [school_id, teacher_id, name, phone, category, biometric_code])
            
            return Response(
                {'message': 'Teacher added successfully'}, 
                status=status.HTTP_201_CREATED
            )
    except Exception as e:
        print(f"Error adding teacher: {e}")
        return Response(
            {'error': 'Failed to add teacher'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['PUT'])
@permission_classes([AllowAny])
def update_teacher(request, school_id, teacher_id):
    """Update teacher details"""
    try:
        data = request.data
        name = data.get('name')
        phone = data.get('phone')
        category = data.get('category')
        biometric_code = data.get('biometric_code', '')
        
        if not all([name, phone, category]):
            return Response(
                {'error': 'Name, phone and category are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE teachers 
                SET name = %s, phone = %s, category = %s, biometric_code = %s
                WHERE school_id = %s AND teacher_id = %s
            """, [name, phone, category, biometric_code, school_id, teacher_id])
            
            if cursor.rowcount == 0:
                return Response(
                    {'error': 'Teacher not found'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            return Response(
                {'message': 'Teacher updated successfully'}, 
                status=status.HTTP_200_OK
            )
    except Exception as e:
        print(f"Error updating teacher: {e}")
        return Response(
            {'error': 'Failed to update teacher'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['DELETE'])
@permission_classes([AllowAny])
def delete_teacher(request, school_id, teacher_id):
    """Delete a teacher"""
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "DELETE FROM teachers WHERE school_id = %s AND teacher_id = %s",
                [school_id, teacher_id]
            )
            
            if cursor.rowcount == 0:
                return Response(
                    {'error': 'Teacher not found'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            return Response(
                {'message': 'Teacher deleted successfully'}, 
                status=status.HTTP_200_OK
            )
    except Exception as e:
        print(f"Error deleting teacher: {e}")
        return Response(
            {'error': 'Failed to delete teacher'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )