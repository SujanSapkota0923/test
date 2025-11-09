from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.db.models import Q, Count
from apps.Course import models
from apps.Course.models import User
from apps.Course.forms import EnrollmentEditForm
from .forms import (
    UserForm, AcademicLevelForm, StreamForm, 
    SubjectForm, LiveClassForm, 
    ExtraCurricularActivityForm, VideoForm, UserLoginForm
)
# ============================================
# basic page rendering views
# ============================================


@login_required
def course_home_view(request):
    extra_activities = models.ExtraCurricularActivity.objects.all()
    extra_activity_count = extra_activities.count()
    limited_activities = extra_activities[:3]
    context = {
        'extra_activities': extra_activities,
        'extra_activity_count': extra_activity_count,
        'limited_activities': limited_activities
    }
    return render(request, 'dashboard/course_home.html', context)

@login_required
def class_level_view(request, level_slug):
    level = models.AcademicLevel.objects.filter(slug=level_slug).first()
    if not level:
        messages.error(request, "Academic level not found.")    
        return redirect('dashboard:index')
    users = models.User.objects.filter(academic_level=level)
    context = {
        'level': level,
        'level_users': users,
    }
    return render(request, 'dashboard/classes.html', context)

@login_required
def subject_list_view(request):
    subjects = models.Subject.objects.all()
    context = {
        'subjects': subjects,
        'subject_count': subjects.count(),
        'limited_subjects': subjects[:3],
    }
    return render(request, 'dashboard/subjects.html', context)

@login_required
def student_list_view(request):
    all_users = models.User.objects.all()

    # Count users by role (single DB query)
    queryset_results = all_users.values('role').annotate(user_count=Count('role'))
    role_counts = {item['role']: item['user_count'] for item in queryset_results}

    total_users = sum(role_counts.values())
    admin_count = role_counts.get(User.Role.ADMIN, 0)
    teacher_count = role_counts.get(User.Role.TEACHER, 0)
    student_count = role_counts.get(User.Role.STUDENT, 0)

    # Separate users in Python (no new queries)
    teachers = [user for user in all_users if user.role == User.Role.TEACHER]
    students = [user for user in all_users if user.role == User.Role.STUDENT]

    context = {
        'total': total_users,
        'admin_count': admin_count,
        'teacher_count': teacher_count,
        'student_count': student_count,
        'teachers': teachers,
        'students': students,
    }
    return render(request, 'dashboard/students.html', context)

@login_required
def teacher_list_view(request):
    all_users = User.objects.all()

    # Count users by role (single DB query)
    queryset_results = all_users.values('role').annotate(user_count=Count('role'))
    role_counts = {item['role']: item['user_count'] for item in queryset_results}

    total_users = sum(role_counts.values())
    admin_count = role_counts.get(User.Role.ADMIN, 0)
    teacher_count = role_counts.get(User.Role.TEACHER, 0)
    student_count = role_counts.get(User.Role.STUDENT, 0)

    # Separate users in Python (no new queries)
    teachers = [user for user in all_users if user.role == User.Role.TEACHER]
    students = [user for user in all_users if user.role == User.Role.STUDENT]

    context = {
        'total': total_users,
        'admin_count': admin_count,
        'teacher_count': teacher_count,
        'student_count': student_count,
        'teachers': teachers,
        'students': students,
    }
    return render(request, 'dashboard/teachers.html', context)

@login_required
def stream_list_view(request):
    streams = models.Stream.objects.all().order_by('-pk')
    context={
        'streams': streams,
        'stream_count': streams.count(),
        'limited_streams': streams[:3],
    }
    return render(request, 'dashboard/streams.html', context)

@login_required
def video_list_view(request):
    videos = models.Video.objects.all().order_by('-pk')
    context={
        'videos': videos,
        'video_count': videos.count(),
        'limited_videos': videos[:3],
    }
    return render(request, 'dashboard/video.html', context)

@login_required
def enrollment_list_view(request):
    enrolled_students=models.User.objects.filter(role=models.User.Role.STUDENT, academic_level__isnull=True)
    # students registered but not enrolled in any class
    context = {
        'enrollmentss': enrolled_students,
    }
    return render(request, 'dashboard/enrollments.html', context)   



@login_required
def live_classes_view(request):

    live_classes = models.LiveClass.objects.all().order_by('-pk')
    context = {
        'live_classes': live_classes,
        'live_class_count': live_classes.count(),
        'limited_live_classes': live_classes[:3],
    }

    return render(request, 'dashboard/liveclasses.html', context)


# from django.contrib.auth.decorators import login_required
from django.db.models import Count
# from django.shortcuts import render
# from . import models


@login_required
def dashboard_view(request):
    context = {}

    # === 1. User Statistics ===
    all_users = User.objects.all()

    # Count users by role (single DB query)
    queryset_results = all_users.values('role').annotate(user_count=Count('role'))
    role_counts = {item['role']: item['user_count'] for item in queryset_results}

    total_users = sum(role_counts.values())
    admin_count = role_counts.get(User.Role.ADMIN, 0)
    teacher_count = role_counts.get(User.Role.TEACHER, 0)
    student_count = role_counts.get(User.Role.STUDENT, 0)

    # Separate users in Python (no new queries)
    teachers = [user for user in all_users if user.role == User.Role.TEACHER]
    students = [user for user in all_users if user.role == User.Role.STUDENT]

    context.update({
        'total': total_users,
        'admin_count': admin_count,
        'teacher_count': teacher_count,
        'student_count': student_count,
        'teachers': teachers,
        'students': students,
    })

    # === 2. Extra Curricular Activities ===
    extra_activities = models.ExtraCurricularActivity.objects.all()
    context.update({
        'extra_activities': extra_activities,
        'extra_activity_count': extra_activities.count(),
        'limited_activities': extra_activities[:3],
    })

    # === 3. Academic Levels ===
    levels = models.AcademicLevel.objects.all().order_by('-pk')
    limited_levels = levels[:3]
    context.update({
        'levels': levels,
        'level_count': levels.count(),
        'limited_levels': limited_levels,
        'capacity_remaining': [
            level.capacity_remaining for level in limited_levels
            if level.capacity_remaining is not None
        ],
    })

    # === 4. Subjects ===
    subjects = models.Subject.objects.all()
    context.update({
        'subjects': subjects,
        'subject_count': subjects.count(),
        'limited_subjects': subjects[:3],
    })

    # # === 5. Streams ===
    # streams = Stream.objects.all().order_by('-pk')
    # context.update({
    #     'streams': streams,
    #     'stream_count': streams.count(),
    #     'limited_streams': streams[:3],
    # })

    # # === 6. Live Classes ===
    # live_classes = LiveClass.objects.all().order_by('-pk')
    # context.update({
    #     'live_classes': live_classes,
    #     'live_class_count': live_classes.count(),
    #     'limited_live_classes': live_classes[:3],
    # })

    # === 7. Videos ===
    videos = models.Video.objects.all().order_by('-pk')
    context.update({
        'videos': videos,
        'video_count': videos.count(),
        'limited_videos': videos[:3],
    })

    return render(request, 'dashboard/index.html', context)








# ============================================
# AUTHENTICATION VIEWS
# ============================================





# def sign_up(request):
#     if request.method == 'POST':
#         form = UserSignUpForm(request.POST, request.FILES)
#         if form.is_valid():
#             form.save()
#             messages.success(request, "Account created successfully! You can now log in.")
#             return redirect('dashboard:login')
#         else:
#             messages.error(request, "Please correct the errors below.")
#     else:
#         form = UserSignUpForm()

#     return render(request, 'dashboard/signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = UserLoginForm(request.POST or None)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            
            # Check if user exists first
            if user is None:
                messages.error(request, "Invalid username or password.")
                return redirect('dashboard:login')
            
            # Now check permissions
            if user.is_superuser or user.role == models.User.Role.ADMIN:
                login(request, user)
                messages.success(request, f"Welcome back, {user.get_full_name() or user.username}!")
                return redirect('dashboard:index')  # ← This was missing!
            else:
                messages.error(request, "You do not have permission to access the dashboard.")
                return redirect('dashboard:login')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = UserLoginForm()

    return render(request, 'dashboard/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('dashboard:login')







# ============================================
# all curd operations for course, user, academic level, stream, subject, enrollment, live class, extra curricular activity, video etc
# ============================================



# ============================================
# USER VIEWS
# ============================================


@login_required
def user_detail(request, pk):
    user = get_object_or_404(models.User, pk=pk)
    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, f'User "{user.username}" updated successfully!')
            return redirect('dashboard:user_detail', pk=pk)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserForm(instance=user)
    
    context = {
        'form': form,
        'item_name': 'User',
        'delete_url': reverse('dashboard:user_delete', args=[pk]),
        'object': user
    }
    return render(request, 'dashboard/detailed.html', context)


# if user is created, it will call add_user view from Course app views.py

# @login_required
# def user_create(request):
#     if request.method == 'POST':
#         form = UserCreateForm(request.POST, request.FILES)
#         if form.is_valid():
#             user = form.save()
#             messages.success(request, f'User "{user.username}" created successfully!')
#             return redirect('dashboard:user_detail', pk=user.pk)
#         else:
#             messages.error(request, 'Please correct the errors below.')
#     else:
#         form = UserCreateForm()
    
#     context = {'form': form, 'item_name': 'User'}
#     return render(request, 'dashboard/add_item.html', context)

@login_required
def user_delete(request, pk):
    user = get_object_or_404(models.User, pk=pk)
    if request.method == 'POST':
        username = user.username
        # user.delete()
        # user should be removed from academic level and stream only
        user.academic_level = None
        user.stream = None
        user.save()
        messages.success(request, f'User "{username}" removed successfully!')
        return redirect('dashboard:index')
    return redirect('dashboard:user_detail', pk=pk)


# ============================================
# ACADEMIC LEVEL VIEWS
# ============================================
# @login_required
# def level_list(request):
#     levels = AcademicLevel.objects.all()
#     context = {'levels': levels, 'item_name': 'Academic Level'}
#     return render(request, 'dashboard/level_list.html', context)

@login_required
def level_detail(request, pk):
    level = get_object_or_404(models.AcademicLevel, pk=pk)
    if request.method == 'POST':
        form = AcademicLevelForm(request.POST, instance=level)
        if form.is_valid():
            form.save()
            messages.success(request, f'Level "{level.name}" updated successfully!')
            return redirect('dashboard:level_detail', pk=pk)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = AcademicLevelForm(instance=level)
    
    context = {
        'form': form,
        'item_name': 'Academic Level',
        'delete_url': reverse('dashboard:level_delete', args=[pk]),
        'object': level
    }
    return render(request, 'dashboard/detailed.html', context)

# @login_required
# def level_create(request):
#     if request.method == 'POST':
#         form = AcademicLevelForm(request.POST)
#         if form.is_valid():
#             level = form.save()
#             messages.success(request, f'Level "{level.name}" created successfully!')
#             return redirect('dashboard:level_detail', pk=level.pk)
#         else:
#             messages.error(request, 'Please correct the errors below.')
#     else:
#         form = AcademicLevelForm()
    
#     context = {'form': form, 'item_name': 'Academic Level'}
#     return render(request, 'dashboard/add_item.html', context)

@login_required
def level_delete(request, pk):
    level = get_object_or_404(models.AcademicLevel, pk=pk)
    if request.method == 'POST':
        name = level.name
        level.delete()
        messages.success(request, f'Level "{name}" deleted successfully!')
        return redirect('dashboard:index')
    return redirect('dashboard:level_detail', pk=pk)


# ============================================
# STREAM VIEWS
# ============================================
# @login_required
# def stream_list(request):
#     streams = Stream.objects.all()
#     context = {'streams': streams, 'item_name': 'Stream'}
#     return render(request, 'dashboard/stream_list.html', context)

@login_required
def stream_detail(request, pk):
    stream = get_object_or_404(models.Stream, pk=pk)
    if request.method == 'POST':
        form = StreamForm(request.POST, instance=stream)
        if form.is_valid():
            form.save()
            messages.success(request, f'Stream "{stream.name}" updated successfully!')
            return redirect('dashboard:stream_detail', pk=pk)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = StreamForm(instance=stream)
    
    context = {
        'form': form,
        'item_name': 'Stream',
        'delete_url': reverse('dashboard:stream_delete', args=[pk]),
        'object': stream
    }
    return render(request, 'dashboard/detailed.html', context)

# @login_required
# def stream_create(request):
#     if request.method == 'POST':
#         form = StreamForm(request.POST)
#         if form.is_valid():
#             stream = form.save()
#             messages.success(request, f'Stream "{stream.name}" created successfully!')
#             return redirect('dashboard:stream_detail', pk=stream.pk)
#         else:
#             messages.error(request, 'Please correct the errors below.')
#     else:
#         form = StreamForm()
    
#     context = {'form': form, 'item_name': 'Stream'}
#     return render(request, 'dashboard/add_item.html', context)

@login_required
def stream_delete(request, pk):
    stream = get_object_or_404(models.Stream, pk=pk)
    if request.method == 'POST':
        name = stream.name
        stream.delete()
        messages.success(request, f'Stream "{name}" deleted successfully!')
        return redirect('dashboard:stream_home')
    return redirect('dashboard:stream_detail', pk=pk)


# ============================================
# SUBJECT VIEWS
# ============================================
# @login_required
# def subject_list(request):
#     subjects = Subject.objects.all()
#     context = {'subjects': subjects, 'item_name': 'Subject'}
#     return render(request, 'dashboard/subject_list.html', context)

@login_required
def subject_detail(request, pk):
    subject = get_object_or_404(models.Subject, pk=pk)
    if request.method == 'POST':
        form = SubjectForm(request.POST, instance=subject)
        if form.is_valid():
            form.save()
            messages.success(request, f'Subject "{subject.name}" updated successfully!')
            return redirect('dashboard:subject_detail', pk=pk)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = SubjectForm(instance=subject)
    
    context = {
        'form': form,
        'item_name': 'Subject',
        'delete_url': reverse('dashboard:subject_delete', args=[pk]),
        'object': subject
    }
    return render(request, 'dashboard/detailed.html', context)

# @login_required
# def subject_create(request):
#     if request.method == 'POST':
#         form = SubjectForm(request.POST)
#         if form.is_valid():
#             subject = form.save()
#             messages.success(request, f'Subject "{subject.name}" created successfully!')
#             return redirect('dashboard:subject_detail', pk=subject.pk)
#         else:
#             messages.error(request, 'Please correct the errors below.')
#     else:
#         form = SubjectForm()
    
#     context = {'form': form, 'item_name': 'Subject'}
#     return render(request, 'dashboard/add_item.html', context)

@login_required
def subject_delete(request, pk):
    subject = get_object_or_404(models.Subject, pk=pk)
    if request.method == 'POST':
        name = subject.name
        subject.delete()
        messages.success(request, f'Subject "{name}" deleted successfully!')
        return redirect('dashboard:subject_home')
    return redirect('dashboard:subject_detail', pk=pk)


# ============================================
# ENROLLMENT VIEWS
# ============================================
# @login_required
# def enrollment_list(request):
#     enrollments = Enrollment.objects.all().select_related('student', 'level')
#     context = {'enrollments': enrollments, 'item_name': 'Enrollment'}
#     return render(request, 'dashboard/enrollment_list.html', context)

@login_required
def enrollment_detail(request, pk):
    enrollment = get_object_or_404(models.User, pk=pk)
    if request.method == 'POST':
        form = EnrollmentEditForm(request.POST, user_instance=enrollment)
        if form.is_valid():
            form.save()
            messages.success(request, f'Academic level updated successfully for {enrollment.get_full_name() or enrollment.username}!')
            return redirect('dashboard:enrollment_detail', pk=pk)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = EnrollmentEditForm(user_instance=enrollment)
    
    context = {
        'form': form,
        'item_name': 'Enrollment',
        'delete_url': reverse('dashboard:enrollment_delete', args=[pk]),
        'object': enrollment
    }
    return render(request, 'dashboard/detailed.html', context)

# @login_required
# def enrollment_create(request):
#     if request.method == 'POST':
#         form = EnrollmentForm(request.POST)
#         if form.is_valid():
#             enrollment = form.save()
#             messages.success(request, f'Enrollment created successfully!')
#             return redirect('dashboard:enrollment_detail', pk=enrollment.pk)
#         else:
#             messages.error(request, 'Please correct the errors below.')
#     else:
#         form = EnrollmentForm()
    
#     context = {'form': form, 'item_name': 'Enrollment'}
#     return render(request, 'dashboard/add_item.html', context)

@login_required
def enrollment_delete(request, pk):
    enrollment = get_object_or_404(models.Enrollment, pk=pk)
    if request.method == 'POST':
        enrollment.delete()
        messages.success(request, f'Enrollment deleted successfully!')
        return redirect('dashboard:enrollment_home')
    return redirect('dashboard:enrollment_detail', pk=pk)


# ============================================
# LIVE CLASS VIEWS
# ============================================
@login_required
# def liveclass_list(request):
#     live_classes = LiveClass.objects.all()
#     context = {'live_classes': live_classes, 'item_name': 'Live Class'}
#     return render(request, 'dashboard/liveclass_list.html', context)

@login_required
def liveclass_detail(request, pk):
    live_class = get_object_or_404(models.LiveClass, pk=pk)
    if request.method == 'POST':
        form = LiveClassForm(request.POST, instance=live_class)
        if form.is_valid():
            form.save()
            messages.success(request, f'Live Class "{live_class.title}" updated successfully!')
            return redirect('dashboard:liveclass_detail', pk=pk)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = LiveClassForm(instance=live_class)
    
    context = {
        'form': form,
        'item_name': 'Live Class',
        'delete_url': reverse('dashboard:liveclass_delete', args=[pk]),
        'object': live_class
    }
    return render(request, 'dashboard/detailed.html', context)

# @login_required
# def liveclass_create(request):
#     if request.method == 'POST':
#         form = LiveClassForm(request.POST)
#         if form.is_valid():
#             live_class = form.save()
#             messages.success(request, f'Live Class "{live_class.title}" created successfully!')
#             return redirect('dashboard:liveclass_detail', pk=live_class.pk)
#         else:
#             messages.error(request, 'Please correct the errors below.')
#     else:
#         form = LiveClassForm()
    
#     context = {'form': form, 'item_name': 'Live Class'}
#     return render(request, 'dashboard/add_item.html', context)

@login_required
def liveclass_delete(request, pk):
    live_class = get_object_or_404(models.LiveClass, pk=pk)
    if request.method == 'POST':
        title = live_class.title
        live_class.delete()
        messages.success(request, f'Live Class "{title}" deleted successfully!')
        return redirect('dashboard:live_classes')
    return redirect('dashboard:liveclass_detail', pk=pk)


# ============================================
# EXTRA CURRICULAR ACTIVITY VIEWS
# ============================================
# @login_required
# def activity_list(request):
#     activities = ExtraCurricularActivity.objects.all()
#     context = {'activities': activities, 'item_name': 'Activity'}
#     return render(request, 'dashboard/activity_list.html', context)
@login_required
def activity_detail(request, pk):
    activity = get_object_or_404(models.ExtraCurricularActivity, pk=pk)
    if request.method == 'POST':
        form = ExtraCurricularActivityForm(request.POST, request.FILES, instance=activity)
        
        if form.is_valid():
            form.save()
            messages.success(request, f'Activity "{activity.title}" and related videos updated successfully!')
            return redirect('dashboard:activity_detail', pk=pk)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ExtraCurricularActivityForm(instance=activity)
    
    context = {
        'form': form,
        'item_name': 'Activity',
        'delete_url': reverse('dashboard:activity_delete', args=[pk]),
        'object': activity
    }
    return render(request, 'dashboard/detailed.html', context)

# @login_required
# def activity_create(request):
#     if request.method == 'POST':
#         form = ExtraCurricularActivityForm(request.POST, request.FILES)
#         if form.is_valid():
#             activity = form.save()
#             messages.success(request, f'Activity "{activity.title}" created successfully!')
#             return redirect('dashboard:activity_detail', pk=activity.pk)
#         else:
#             messages.error(request, 'Please correct the errors below.')
#     else:
#         form = ExtraCurricularActivityForm()
    
#     context = {'form': form, 'item_name': 'Activity'}
#     return render(request, 'dashboard/add_item.html', context)

@login_required
def activity_delete(request, pk):
    activity = get_object_or_404(models.ExtraCurricularActivity, pk=pk)
    if request.method == 'POST':
        title = activity.title
        activity.delete()
        messages.success(request, f'Activity "{title}" deleted successfully!')
        return redirect('dashboard:course_home')
    return redirect('dashboard:activity_detail', pk=pk)


# ============================================
# VIDEO VIEWS
# ============================================
# @login_required
# def video_list(request):
#     videos = Video.objects.all()
#     context = {'videos': videos, 'item_name': 'Video'}
#     return render(request, 'dashboard/video_list.html', context)

@login_required
def video_detail(request, pk):
    video = get_object_or_404(models.Video, pk=pk)
    if request.method == 'POST':
        form = VideoForm(request.POST, request.FILES, instance=video)
        if form.is_valid():
            form.save()
            messages.success(request, f'Video "{video.title}" updated successfully!')
            return redirect('dashboard:video_detail', pk=pk)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = VideoForm(instance=video)
    
    context = {
        'form': form,
        'item_name': 'Video',
        'delete_url': reverse('dashboard:video_delete', args=[pk]),
        'object': video
    }
    return render(request, 'dashboard/detailed.html', context)

# @login_required
# def video_create(request):
#     if request.method == 'POST':
#         form = VideoForm(request.POST, request.FILES)
#         if form.is_valid():
#             video = form.save()
#             messages.success(request, f'Video "{video.title}" created successfully!')
#             return redirect('dashboard:video_detail', pk=video.pk)
#         else:
#             messages.error(request, 'Please correct the errors below.')
#     else:
#         form = VideoForm()
    
#     context = {'form': form, 'item_name': 'Video'}
#     return render(request, 'dashboard/add_item.html', context)

@login_required
def video_delete(request, pk):
    video = get_object_or_404(models.Video, pk=pk)
    if request.method == 'POST':
        title = video.title
        video.delete()
        messages.success(request, f'Video "{title}" deleted successfully!')
        return redirect('dashboard:video_home')
    return redirect('dashboard:video_detail', pk=pk)


# ============================================
# Global Search View
# ============================================

@login_required
def global_search_view(request):
    query = request.GET.get('q', '').strip()
    results = {
        'query': query,
        'users': [],
        'students': [],
        'teachers': [],
        'courses': [],
        'subjects': [],
        'levels': [],
        'streams': [],
        'videos': [],
        'live_classes': [],
        'enrollments': [],
        'error': None,
    }
    
    if not query:
        return render(request, 'dashboard/search_results.html', results)
    
    # Parse search query for prefixes like "user:", "student:", etc.
    search_type = None
    search_term = query
    
    # Map prefixes to search types
    prefix_map = {
        'user': 'users',
        'users': 'users',
        'student': 'students',
        'students': 'students',
        'teacher': 'teachers',
        'teachers': 'teachers',
        'course': 'courses',
        'courses': 'courses',
        'subject': 'subjects',
        'subjects': 'subjects',
        'level': 'levels',
        'levels': 'levels',
        'class': 'levels',
        'classes': 'levels',
        'stream': 'streams',
        'streams': 'streams',
        'video': 'videos',
        'videos': 'videos',
        'live': 'live_classes',
        'enrollment': 'enrollments',
        'enrollments': 'enrollments',
    }
    
    if ':' in query:
        parts = query.split(':', 1)
        if len(parts) == 2:
            prefix = parts[0].lower().strip()
            term = parts[1].strip()
            
            # Only use prefix if it's a valid search type AND term is not empty
            if prefix in prefix_map and term:
                search_type = prefix_map[prefix]
                search_term = term
    
    # If no specific type or invalid prefix, search all with original query
    if not search_type:
        search_term = query
    
    # If search_term is empty after parsing, use original query
    if not search_term:
        search_term = query
    
    # Determine which categories to search
    search_all = (search_type is None)
    
    try:
        
        # Search Users (only when specifically requested with "user:" prefix)
        if search_type == 'users':
        
            results['users'] = list(models.User.objects.filter(
                Q(username__icontains=search_term) |
                Q(first_name__icontains=search_term) |
                Q(last_name__icontains=search_term) |
                Q(email__icontains=search_term) |
                Q(phone__icontains=search_term)
            )[:20])
        
        # Search Students only
        if search_all or search_type == 'students':
            results['students'] = list(models.User.objects.filter(
                role=models.User.Role.STUDENT
            ).filter(
                Q(username__icontains=search_term) |
                Q(first_name__icontains=search_term) |
                Q(last_name__icontains=search_term) |
                Q(email__icontains=search_term) |
                Q(phone__icontains=search_term)
            )[:20])
        
        # Search Teachers only
        if search_all or search_type == 'teachers':
            results['teachers'] = list(models.User.objects.filter(
                role=models.User.Role.TEACHER
            ).filter(
                Q(username__icontains=search_term) |
                Q(first_name__icontains=search_term) |
                Q(last_name__icontains=search_term) |
                Q(email__icontains=search_term) |
                Q(phone__icontains=search_term)
            )[:20])
        
        # Search Courses
        if search_all or search_type == 'courses':
            results['courses'] = list(models.ExtraCurricularActivity.objects.filter(
                Q(title__icontains=search_term) |
                Q(description__icontains=search_term)
            )[:20])
        
        # Search Subjects
        if search_all or search_type == 'subjects':
            results['subjects'] = list(models.Subject.objects.filter(
                Q(name__icontains=search_term) |
                Q(description__icontains=search_term)
            )[:20])
        
        # Search Academic Levels
        if search_all or search_type == 'levels':
            results['levels'] = list(models.AcademicLevel.objects.filter(
                Q(name__icontains=search_term) |
                Q(slug__icontains=search_term)
            )[:20])
        
        # Search Streams
        if search_all or search_type == 'streams':
            results['streams'] = list(models.Stream.objects.filter(
                Q(name__icontains=search_term)
            )[:20])
        
        # Search Videos
        if search_all or search_type == 'videos':
            results['videos'] = list(models.Video.objects.filter(
                Q(title__icontains=search_term) |
                Q(description__icontains=search_term)
            )[:20])

        
        # Search Live Classes
        if search_all or search_type == 'live_classes':
            results['live_classes'] = list(models.LiveClass.objects.filter(
                Q(title__icontains=search_term) |
                Q(description__icontains=search_term)
            )[:20])
        
        # Search Enrollments
        if search_all or search_type == 'enrollments':
            results['enrollments'] = list(models.Enrollment.objects.filter(
                Q(student__username__icontains=search_term) |
                Q(student__first_name__icontains=search_term) |
                Q(student__last_name__icontains=search_term) |
                Q(level__name__icontains=search_term)
            )[:20])
    
    except Exception as e:
        # Log the error and show a friendly message
        results['error'] = f"An error occurred during search: {str(e)}"
        import traceback
    
    results['search_type'] = search_type
    results['search_term'] = search_term
    
    return render(request, 'dashboard/search_results.html', results)

