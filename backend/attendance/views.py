from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.db import connection
from datetime import datetime, date, timedelta

@api_view(['GET'])
@permission_classes([AllowAny])
def get_attendance_report(request, school_id):
    """Get attendance report for date range"""
    try:
        start_date = request.GET.get('start_date', str(date.today() - timedelta(days=7)))
        end_date = request.GET.get('end_date', str(date.today()))
        
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    a.date, 
                    a.teacher_id, 
                    t.name as teacher_name,
                    a.status,
                    a.check_in_time,
                    a.check_out_time
                FROM attendance a
                JOIN teachers t ON a.teacher_id = t.teacher_id AND a.school_id = t.school_id
                WHERE a.school_id = %s 
                AND a.date BETWEEN %s AND %s
                ORDER BY a.date DESC, t.name
            """, [school_id, start_date, end_date])
            
            attendance_data = []
            for row in cursor.fetchall():
                attendance_data.append({
                    'date': row[0],
                    'teacher_id': row[1],
                    'teacher_name': row[2],
                    'status': row[3],
                    'check_in_time': row[4],
                    'check_out_time': row[5]
                })
            
            return Response({'attendance': attendance_data}, status=status.HTTP_200_OK)
    except Exception as e:
        print(f"Error fetching attendance report: {e}")
        return Response(
            {'error': 'Failed to fetch attendance report'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([AllowAny])
def mark_attendance(request, school_id):
    """Mark attendance for teachers"""
    try:
        data = request.data
        teacher_id = data.get('teacher_id')
        attendance_date = data.get('date', str(date.today()))
        attendance_status = data.get('status', 'present')
        check_in_time = data.get('check_in_time')
        check_out_time = data.get('check_out_time')
        
        if not teacher_id:
            return Response(
                {'error': 'Teacher ID is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        with connection.cursor() as cursor:
            # Check if attendance already exists
            cursor.execute("""
                SELECT COUNT(*) FROM attendance 
                WHERE school_id = %s AND teacher_id = %s AND date = %s
            """, [school_id, teacher_id, attendance_date])
            
            if cursor.fetchone()[0] > 0:
                # Update existing attendance
                cursor.execute("""
                    UPDATE attendance 
                    SET status = %s, check_in_time = %s, check_out_time = %s
                    WHERE school_id = %s AND teacher_id = %s AND date = %s
                """, [attendance_status, check_in_time, check_out_time, school_id, teacher_id, attendance_date])
            else:
                # Insert new attendance
                cursor.execute("""
                    INSERT INTO attendance (school_id, teacher_id, date, status, check_in_time, check_out_time)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, [school_id, teacher_id, attendance_date, attendance_status, check_in_time, check_out_time])
            
            return Response(
                {'message': 'Attendance marked successfully'}, 
                status=status.HTTP_200_OK
            )
    except Exception as e:
        print(f"Error marking attendance: {e}")
        return Response(
            {'error': 'Failed to mark attendance'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([AllowAny])
def get_daily_attendance(request, school_id):
    """Get attendance for a specific date"""
    try:
        attendance_date = request.GET.get('date', str(date.today()))
        
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    t.teacher_id,
                    t.name,
                    t.category,
                    COALESCE(a.status, 'not_marked') as status,
                    a.check_in_time,
                    a.check_out_time
                FROM teachers t
                LEFT JOIN attendance a ON t.teacher_id = a.teacher_id 
                    AND t.school_id = a.school_id 
                    AND a.date = %s
                WHERE t.school_id = %s
                ORDER BY t.name
            """, [attendance_date, school_id])
            
            daily_attendance = []
            for row in cursor.fetchall():
                daily_attendance.append({
                    'teacher_id': row[0],
                    'name': row[1],
                    'category': row[2],
                    'status': row[3],
                    'check_in_time': row[4],
                    'check_out_time': row[5]
                })
            
            return Response({'daily_attendance': daily_attendance}, status=status.HTTP_200_OK)
    except Exception as e:
        print(f"Error fetching daily attendance: {e}")
        return Response(
            {'error': 'Failed to fetch daily attendance'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )