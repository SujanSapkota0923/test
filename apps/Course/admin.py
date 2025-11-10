from django.contrib import admin

# Register your models here.


from .models import ( 
    User,
    AcademicLevel,
    Stream,
    Subject,
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
    LiveClass, Course, Video
)

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'role', 'academic_level', 'course', 'enrolled', 'is_active', 'date_joined']
    list_filter = ['role', 'is_active', 'academic_level', 'course']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Custom Fields', {'fields': ('role', 'phone', 'bio', 'profile_picture', 'academic_level', 'course')}),
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


from .models import PaymentMethod, PaymentVerification

@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'display_order', 'created_by', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at', 'created_by']
    ordering = ['display_order', 'name']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'image')
        }),
        ('Payment Details', {
            'fields': ('details',),
            'description': 'Enter JSON format data for account numbers, QR codes, etc.'
        }),
        ('Display Settings', {
            'fields': ('is_active', 'display_order')
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:  # If creating new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(PaymentVerification)
class PaymentVerificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'course', 'amount', 'payment_method', 'verified', 'created_at', 'verified_at']
    list_filter = ['verified', 'payment_method', 'created_at', 'verified_at']
    search_fields = ['user__username', 'user__email', 'course__title', 'transaction_id']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Payment Information', {
            'fields': ('user', 'course', 'payment_method', 'amount', 'transaction_id')
        }),
        ('Proof & Remarks', {
            'fields': ('payment_proof', 'remarks')
        }),
        ('Verification', {
            'fields': ('verified', 'verified_by', 'verified_at', 'verification_notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if change and obj.verified and not obj.verified_by:
            obj.verified_by = request.user
            if not obj.verified_at:
                from django.utils import timezone
                obj.verified_at = timezone.now()
            # Enroll user in course
            obj.user.course = obj.course
            obj.user.save()
        super().save_model(request, obj, form, change)
