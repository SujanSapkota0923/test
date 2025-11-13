from collections import OrderedDict
from rest_framework import serializers
from apps.Course.models import Course, AcademicLevel, User, Stream, Subject, LiveClass


class UserCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new user (signup)
    """
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'password',
            'first_name',
            'last_name',
            'bio',
            'profile_picture',
        ]
        extra_kwargs = {
            'bio': {'required': False},
            'profile_picture': {'required': False},
        }

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for viewing/updating user profiles
    Only username is visible to all; other fields are admin-only
    """

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'profile_picture',
        ]
        read_only_fields = ['id', 'username']


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = [
            'id',
            'title',
            'description',
            'cost',
            'start_time',
            'end_time',
            'image',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']


class AcademicLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicLevel
        fields = [
            'id',
            'name',
            'allowed_streams',
            'capacity',
        ]
        read_only_fields = ['id', 'capacity', 'allowed_streams', 'name']


class StreamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stream
        fields = [
            'id',
            'name',
            'level',
        ]
        read_only_fields = ['id', 'name', 'level']

class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = [
            'name',
            'description',
        ]
        read_only_fields = ['name', 'description']
    pass

class LiveClassSerializer(serializers.ModelSerializer):
    """Full serializer for authenticated users"""
    class Meta:
        model = LiveClass
        fields = '__all__'
        read_only_fields = ['id', 'created_at']


class LiveClassPublicSerializer(serializers.ModelSerializer):
    """Limited serializer for unauthenticated users - only name and image"""
    class Meta:
        model = LiveClass
        fields = ['id', 'title']  # Only name (title) visible to public
        read_only_fields = ['id', 'title']

