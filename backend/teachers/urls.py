from django.urls import path
from . import views

urlpatterns = [
    path('<str:school_id>/', views.get_all_teachers, name='get_all_teachers'),
    path('<str:school_id>/add/', views.add_teacher, name='add_teacher'),
    path('<str:school_id>/<str:teacher_id>/update/', views.update_teacher, name='update_teacher'),
    path('<str:school_id>/<str:teacher_id>/delete/', views.delete_teacher, name='delete_teacher'),
]