from django.urls import path
from . import views

urlpatterns = [
    path('<str:school_id>/report/', views.get_attendance_report, name='get_attendance_report'),
    path('<str:school_id>/mark/', views.mark_attendance, name='mark_attendance'),
    path('<str:school_id>/daily/', views.get_daily_attendance, name='get_daily_attendance'),
]