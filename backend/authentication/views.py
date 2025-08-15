from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db import connection
from .models import School, Admin
from .serializers import SchoolSerializer, AdminSerializer
import bcrypt

@api_view(['GET'])
def get_schools(request):
    """Get list of all schools"""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT school_id, school_name, address, email, logourl FROM schools")
            schools_data = cursor.fetchall()

            schools = []
            for school in schools_data:
                schools.append({
                    'school_id': school[0],
                    'school_name': school[1],
                    'address': school[2],
                    'email': school[3],
                    'logourl': school[4]
                })

            return Response({'schools': schools}, status=status.HTTP_200_OK)
    except Exception as e:
        print(f"Error fetching schools: {e}")
        return Response(
            {'error': 'Failed to fetch schools'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
def login(request):
    """Admin login"""
    try:
        school_id = request.data.get('school_id')
        username = request.data.get('username')
        password = request.data.get('password')

        if not all([school_id, username, password]):
            return Response(
                {'error': 'School ID, username and password are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT id, school_id, username, password, name, phone, teacher_id, email FROM admins WHERE school_id = %s AND username = %s",
                [school_id, username]
            )
            admin_data = cursor.fetchone()

            if not admin_data:
                return Response(
                    {'error': 'Invalid credentials'}, 
                    status=status.HTTP_401_UNAUTHORIZED
                )

            # Check password (assuming bcrypt hashed)
            stored_password = admin_data[3]
            if isinstance(stored_password, str):
                stored_password = stored_password.encode('utf-8')

            if isinstance(password, str):
                password = password.encode('utf-8')

            # For now, simple string comparison (you can implement bcrypt later)
            if stored_password.decode('utf-8') == password.decode('utf-8'):
                admin_info = {
                    'id': admin_data[0],
                    'school_id': admin_data[1],
                    'username': admin_data[2],
                    'name': admin_data[4],
                    'phone': admin_data[5],
                    'teacher_id': admin_data[6],
                    'email': admin_data[7]
                }

                # Get school details
                cursor.execute(
                    "SELECT school_name, logourl FROM schools WHERE school_id = %s",
                    [school_id]
                )
                school_data = cursor.fetchone()

                if school_data:
                    admin_info['school_name'] = school_data[0]
                    admin_info['school_logo'] = school_data[1]

                return Response({
                    'message': 'Login successful',
                    'admin': admin_info
                }, status=status.HTTP_200_OK)
            else:
                return Response(
                    {'error': 'Invalid credentials'}, 
                    status=status.HTTP_401_UNAUTHORIZED
                )

    except Exception as e:
        print(f"Login error: {e}")
        return Response(
            {'error': 'Login failed'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )