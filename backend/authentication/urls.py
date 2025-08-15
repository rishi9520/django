
from django.urls import path
from . import views

urlpatterns = [
    path('schools/', views.get_schools, name='get_schools'),
    path('login/', views.login, name='login'),
]
