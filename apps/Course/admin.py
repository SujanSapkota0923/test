from django.contrib import admin

# Register your models here.


from .models import ( 
    User,
    AcademicLevel,
    Stream,
    Subject,
    Enrollment,
    LiveClass
)
# @admin.register(User)
# class UserAdmin(admin.ModelAdmin):
#     list_display = ("username", "email", "role", "is_active", "is_staff")
#     list_filter = ("role", "is_active", "is_staff")
#     search_fields = ("username", "email")

# admin.site.register(AcademicLevel)
# admin.site.register(Stream)
# admin.site.register(Subject)
# admin.site.register(Enrollment)
# admin.site.register(LiveClass)

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    User, AcademicLevel, Stream, Subject, 
    Enrollment, LiveClass, Course, Video
)

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'role', 'academic_level', 'is_active', 'date_joined']
    list_filter = ['role', 'is_active', 'academic_level']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Custom Fields', {'fields': ('role', 'phone', 'bio', 'profile_picture', 'academic_level')}),
    )

@admin.register(AcademicLevel)
class AcademicLevelAdmin(admin.ModelAdmin):
    list_display = ['name', 'order', 'allows_streams', 'capacity', 'capacity_remaining']
    list_filter = ['allows_streams']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['order']

@admin.register(Stream)
class StreamAdmin(admin.ModelAdmin):
    list_display = ['name', 'level', 'slug']
    list_filter = ['level']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'levels']
    list_filter = ['levels']
    search_fields = ['name']
    filter_horizontal = ['streams']

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ['student', 'level', 'joined_at', 'is_active']
    list_filter = ['level', 'is_active', 'joined_at']
    search_fields = ['student__username', 'student__email']
    date_hierarchy = 'joined_at'

@admin.register(LiveClass)
class LiveClassAdmin(admin.ModelAdmin):
    list_display = ['title', 'level', 'subject', 'start_time', 'end_time', 'is_recorded']
    list_filter = ['level', 'subject', 'is_recorded', 'start_time']
    search_fields = ['title', 'description']
    date_hierarchy = 'start_time'
    readonly_fields = ['created_at']

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'start_time', 'end_time', 'created_at']
    list_filter = ['start_time']
    search_fields = ['title', 'description']
    date_hierarchy = 'start_time'
    filter_horizontal = ['participants']

@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ['title', 'level', 'subject', 'teacher', 'cost_display', 'uploaded_at']
    list_filter = ['level', 'subject', 'teacher', 'uploaded_at']
    search_fields = ['title', 'description']
    date_hierarchy = 'uploaded_at'
    filter_horizontal = ['stream']
    readonly_fields = ['uploaded_at']
