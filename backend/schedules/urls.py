from django.urls import path
from . import views

urlpatterns = [
    path('<str:school_id>/', views.get_school_schedule, name='get_school_schedule'),
    path('<str:school_id>/teacher/<str:teacher_id>/', views.get_teacher_schedule, name='get_teacher_schedule'),
]