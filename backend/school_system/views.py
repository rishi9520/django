
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny
from authentication.models import School
from .serializers import SchoolSerializer


class SchoolListView(ListAPIView):
    queryset = School.objects.all()
    serializer_class = SchoolSerializer
    permission_classes = [AllowAny]
