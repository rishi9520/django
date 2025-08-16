from django.urls import path
from . import views

urlpatterns = [
    path('<str:school_id>/absent-teachers/', views.get_absent_teachers, name='get_absent_teachers'),
    path('<str:school_id>/arrangements/', views.get_arrangements, name='get_arrangements'),
    path('<str:school_id>/create-manual/', views.create_manual_arrangement, name='create_manual_arrangement'),
]