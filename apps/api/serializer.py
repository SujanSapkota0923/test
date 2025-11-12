from rest_framework import serializers

from apps.Course.models import Course, User, AcademicLevel


class UserSerializer(serializers.ModelSerializer):
	class Meta:
		model = User
		fields = [
			'username',
			'email',
			'first_name',
			'last_name',
			'is_staff',
			'bio',
			'profile_picture',
		]
		read_only_fields = ['id', 'created_at', 'is_staff', 'username', 'email']

class CourseSerializer(serializers.ModelSerializer):
	class Meta:
		model = Course
		fields = [
			'title',
			'description',
			'cost',
			'start_time',
			'end_time',
			'image',
			'created_at',
		]
		read_only_fields = '__all__fields__'


class AcademicLevelSerializer(serializers.ModelSerializer):
	class Meta:
		model=AcademicLevel
		fields = [
			'id',
			'name',
			'allows_streams',
			'capacity',
		]
		read_only_fields = ['id', 'capacity', 'allowed_streams', 'name']


