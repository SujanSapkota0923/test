from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from apps.Course.models import Course, PaymentMethod, User, AcademicLevel, Stream, Subject, LiveClass, Video
from .serializer import CourseSerializer, PaymentMethodSerializer, UserSerializer, UserCreateSerializer, AcademicLevelSerializer, \
    StreamSerializer, SubjectSerializer, LiveClassSerializer, LiveClassPublicSerializer, VideoSerializer, VideoPublicSerializer


class UserViewSet(ModelViewSet):
    # queryset = User.objects.all()
    # serializer_class = UserSerializer
    # permission_classes = [IsAuthenticated]


    def get_queryset(self):
        queryset = User.objects.filter(id=self.request.user.id)
        return queryset
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer

    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data) 




class CourseViewSet(viewsets.ReadOnlyModelViewSet):
    """Basic Course API for beginners: list, retrieve, create, update, delete."""
    queryset = Course.objects.all().order_by('-start_time')
    serializer_class = CourseSerializer
    permission_classes = [AllowAny]


class AcademicLevelViewSet(viewsets.ModelViewSet):
    """Basic Academic Level API for beginners: list, retrieve, create, update, delete."""
    queryset = AcademicLevel.objects.all()
    serializer_class = AcademicLevelSerializer
    permission_classes = [AllowAny]
    http_method_names = ['get']  # Restrict to read-only methods or can use abstraction just like of courseviewset


class StreamViewSet(viewsets.ReadOnlyModelViewSet):
    """Basic Stream API for beginners: list, retrieve, create, update, delete."""
    queryset = Stream.objects.all()
    serializer_class = StreamSerializer
    permission_classes = [AllowAny]
    # http_method_names = ['get']  # Restrict to read-only methods or can use abstraction just like of courseviewset

class SubjectViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    permission_classes = [AllowAny]


class LiveClassViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = LiveClass.objects.all() # all live classes 
    permission_classes = [AllowAny]

    def get_serializer_class(self):
        if self.request.user.is_authenticated:
            return LiveClassSerializer
        return LiveClassPublicSerializer

    def list(self, request, *args, **kwargs):
        user = request.user
        if user.is_authenticated:
            enrolled_courses = user.course
            enrolled_live_classes = LiveClass.objects.filter(course=enrolled_courses)
            other_live_classes = LiveClass.objects.exclude(course=enrolled_courses)
            enrolled_serializer = LiveClassSerializer(enrolled_live_classes, many=True)
            other_serializer = LiveClassPublicSerializer(other_live_classes, many=True)
            
            combined_data = {
                'enrolled_live_classes': enrolled_serializer.data,
                'other_live_classes': other_serializer.data
            }
            
            return Response(combined_data)
        else:
            queryset = self.get_queryset()
            serializer = LiveClassPublicSerializer(queryset, many=True)
            return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()  # Get the live class instance
        
        if request.user.is_authenticated:
            # Check if user is enrolled in the course that contains this live class
            if request.user.course == instance.course:
                serializer = LiveClassSerializer(instance)
            else:
                serializer = LiveClassPublicSerializer(instance)
        else:
            serializer = LiveClassPublicSerializer(instance)
        
        return Response(serializer.data)

class VideoViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Video.objects.all()
    permission_classes = [AllowAny]

    def get_serializer_class(self):
        if self.request.user.is_authenticated:
            return VideoSerializer
        return VideoPublicSerializer

    # simlar logic as in liveclassviewset is applied here for list and retrieve methods
    def list(self, request, *args, **kwargs):
        user = request.user
        if user.is_authenticated:
            enrolled_courses = user.course
            enrolled_videos = Video.objects.filter(course=enrolled_courses)
            other_videos = Video.objects.exclude(course=enrolled_courses)
            enrolled_serializer = VideoSerializer(enrolled_videos, many=True)
            other_serializer = VideoPublicSerializer(other_videos, many=True)
            
            combined_data = {
                'enrolled_videos': enrolled_serializer.data,
                'other_videos': other_serializer.data
            }
            
            return Response(combined_data)
        else:
            queryset = self.get_queryset()
            serializer = VideoPublicSerializer(queryset, many=True)
            return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()  # Get the Video instance
        
        if request.user.is_authenticated:
            # Check if user is enrolled in the course that contains this video
            if request.user.course == instance.course:
                serializer = VideoSerializer(instance)
            else:
                serializer = VideoPublicSerializer(instance)
        else:
            serializer = VideoPublicSerializer(instance)
        
        return Response(serializer.data)
    
class PaymentMethodViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PaymentMethod.objects.all()
    serializer_class = PaymentMethodSerializer
    permission_classes = [AllowAny]
    

    

