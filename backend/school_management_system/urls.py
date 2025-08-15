
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('authentication.urls')),
    path('api/teachers/', include('teachers.urls')),
    path('api/arrangements/', include('arrangements.urls')),
    path('api/attendance/', include('attendance.urls')),
    path('api/schedules/', include('schedules.urls')),
]
