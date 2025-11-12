
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from apps.Course.models import Course, User, AcademicLevel
from .serializer import CourseSerializer, UserSerializer, AcademicLevelSerializer
from .utility import IsadminOnly


class UserViewSet(viewsets.ModelViewSet):
	"""Basic User API for beginners: list, retrieve, create, update, delete."""
	queryset = User.objects.all().order_by('-date_joined')
	serializer_class = UserSerializer
	permission_classes = [IsAuthenticatedOrReadOnly]


class CourseViewSet(viewsets.ModelViewSet):
	"""Basic Course API for beginners: list, retrieve, create, update, delete."""
	queryset = Course.objects.all().order_by('-start_time')
	serializer_class = CourseSerializer
	permission_classes = [IsadminOnly]

class AcademicLevelViewSet(viewsets.ModelViewSet):
	"""Basic Academic Level API for beginners: list, retrieve, create, update, delete."""
	queryset = AcademicLevel.objects.all()
	serializer_class = AcademicLevelSerializer
	permission_classes = [IsadminOnly]


