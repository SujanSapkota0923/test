from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.db.models import Q, Count
from apps.Course import models
from apps.Course.models import User
from .forms import (
    UserForm, AcademicLevelForm, StreamForm, 
    SubjectForm, LiveClassForm, 
    CourseForm, VideoForm, UserLoginForm
)
# ============================================
# basic page rendering views
# ============================================


@login_required
def course_home_view(request):
    # Optimize query with prefetch_related for enrolled_students (from User.course ForeignKey)
    extra_activities = models.Course.objects.all().prefetch_related('enrolled_students').annotate(
        participant_count=Count('enrolled_students')
    ).order_by('-created_at')
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
    level = models.AcademicLevel.objects.prefetch_related('streams', 'subjects').filter(slug=level_slug).first()
    if not level:
        messages.error(request, "Academic level not found.")    
        return redirect('dashboard:index')
    users = models.User.objects.filter(academic_level=level).select_related('course')
    
    # Get statistics
    total_students = users.filter(role=User.Role.STUDENT).count()
    enrolled_students = users.filter(role=User.Role.STUDENT, course__isnull=False).count()
    
    context = {
        'level': level,
        'level_users': users,
        'total_students': total_students,
        'enrolled_students': enrolled_students,
        'unenrolled_students': total_students - enrolled_students,
    }
    return render(request, 'dashboard/classes.html', context)

@login_required
def subject_list_view(request):
    # Optimize query with select_related and prefetch_related
    subjects = models.Subject.objects.select_related('levels').prefetch_related('streams').all()
    context = {
        'subjects': subjects,
        'subject_count': subjects.count(),
        'limited_subjects': subjects[:3],
    }
    return render(request, 'dashboard/subjects.html', context)

@login_required
def student_list_view(request):
    # Optimize query with select_related for academic_level and course
    all_users = models.User.objects.select_related('academic_level', 'course').all()

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
    
    # Calculate student statistics
    enrolled_students = sum(1 for s in students if s.course is not None)
    active_students = sum(1 for s in students if s.is_active)

    context = {
        'total': total_users,
        'admin_count': admin_count,
        'teacher_count': teacher_count,
        'student_count': student_count,
        'teachers': teachers,
        'students': students,
        'enrolled_students': enrolled_students,
        'active_students': active_students,
    }
    return render(request, 'dashboard/students.html', context)

@login_required
def teacher_list_view(request):
    # Optimize query with select_related for academic_level
    all_users = User.objects.select_related('academic_level').all()

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
    
    # Calculate teacher statistics
    active_teachers = sum(1 for t in teachers if t.is_active)
    
    # Count videos and live classes by teachers
    videos_by_teachers = models.Video.objects.filter(teacher__in=[t.id for t in teachers]).values('teacher').annotate(video_count=Count('id'))
    video_counts = {item['teacher']: item['video_count'] for item in videos_by_teachers}
    
    live_classes_by_teachers = models.LiveClass.objects.filter(hosts__in=[t.id for t in teachers]).values('hosts').annotate(class_count=Count('id'))
    class_counts = {item['hosts']: item['class_count'] for item in live_classes_by_teachers}

    context = {
        'total': total_users,
        'admin_count': admin_count,
        'teacher_count': teacher_count,
        'student_count': student_count,
        'teachers': teachers,
        'students': students,
        'active_teachers': active_teachers,
        'video_counts': video_counts,
        'class_counts': class_counts,
    }
    return render(request, 'dashboard/teachers.html', context)

@login_required
def stream_list_view(request):
    # Optimize with select_related for level and annotate subject count
    streams = models.Stream.objects.select_related('level').annotate(
        subject_count=Count('subjects')
    ).order_by('-pk')
    context={
        'streams': streams,
        'stream_count': streams.count(),
        'limited_streams': streams[:3],
    }
    return render(request, 'dashboard/streams.html', context)

@login_required
def video_list_view(request):
    # Optimize with select_related and prefetch_related
    videos = models.Video.objects.select_related(
        'subject', 'teacher', 'course', 'level'
    ).prefetch_related('stream').order_by('-uploaded_at')
    context={
        'videos': videos,
        'video_count': videos.count(),
        'limited_videos': videos[:3],
    }
    return render(request, 'dashboard/video.html', context)

@login_required
def enrollment_list_view(request):
    # Get all students with optimization
    all_students = models.User.objects.filter(
        role=models.User.Role.STUDENT
    ).select_related('academic_level', 'course').order_by('-date_joined')
    
    # Students who are NOT enrolled in any course (course is NULL)
    unenrolled_students = all_students.filter(course__isnull=True)
    
    # Students who ARE enrolled in a course
    enrolled_students = all_students.filter(course__isnull=False)
    
    # Statistics
    total_students = all_students.count()
    enrolled_count = enrolled_students.count()
    unenrolled_count = unenrolled_students.count()
    active_enrolled = enrolled_students.filter(is_active=True).count()
    
    # Get enrollment by course
    enrollments_by_course = enrolled_students.values('course__title').annotate(
        count=Count('id')
    ).order_by('-count')[:5]
    
    context = {
        'all_students': all_students,
        'enrolled_students': enrolled_students,
        'unenrolled_students': unenrolled_students,
        'total_students': total_students,
        'enrolled_count': enrolled_count,
        'unenrolled_count': unenrolled_count,
        'active_enrolled': active_enrolled,
        'enrollments_by_course': enrollments_by_course,
    }
    return render(request, 'dashboard/enrollments.html', context)   



@login_required
def live_classes_view(request):
    # Optimize with select_related for related fields
    live_classes = models.LiveClass.objects.select_related(
        'subject', 'hosts', 'level', 'course'
    ).order_by('-start_time')
    context = {
        'live_classes': live_classes,
        'live_class_count': live_classes.count(),
        'limited_live_classes': live_classes[:3],
    }
    
    return render(request, 'dashboard/liveclasses.html', context)


@login_required
def payment_method_list(request):
    payment_methods = models.PaymentMethod.objects.all()
    context = {
        'payment_methods': payment_methods,
    }
    return render(request, 'dashboard/payment_methods.html', context)


@login_required
def add_payment_method(request):
    from .forms import PaymentMethodForm
    if request.method == 'POST':
        form = PaymentMethodForm(request.POST, request.FILES)
        if form.is_valid():
            payment_method = form.save(commit=False)
            payment_method.created_by = request.user
            payment_method.save()
            messages.success(request, f'Payment method "{payment_method.name}" has been added successfully.')
            return redirect('dashboard:payment_method_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PaymentMethodForm()
    
    context = {
        'form': form,
        'item_name': 'Payment Method',
    }
    return render(request, 'dashboard/add_item.html', context)


@login_required
def payment_method_detail(request, pk):
    from .forms import PaymentMethodForm
    payment_method = get_object_or_404(models.PaymentMethod, pk=pk)
    form = PaymentMethodForm(instance=payment_method)
    
    context = {
        'payment_method': payment_method,
        'object': payment_method,
        'form': form,
        'item_name': 'Payment Method',
    }
    return render(request, 'dashboard/detailed.html', context)


@login_required
def edit_payment_method(request, pk):
    from .forms import PaymentMethodForm
    payment_method = get_object_or_404(models.PaymentMethod, pk=pk)
    
    if request.method == 'POST':
        form = PaymentMethodForm(request.POST, request.FILES, instance=payment_method)
        if form.is_valid():
            form.save()
            messages.success(request, f'Payment method "{payment_method.name}" has been updated successfully.')
            return redirect('dashboard:payment_method_detail', pk=pk)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PaymentMethodForm(instance=payment_method)
    
    context = {
        'form': form,
        'item_name': 'Payment Method',
        'is_edit': True,
        'object': payment_method,
    }
    return render(request, 'dashboard/add_item.html', context)


@login_required
def delete_payment_method(request, pk):
    payment_method = get_object_or_404(models.PaymentMethod, pk=pk)
    
    if request.method == 'POST':
        name = payment_method.name
        payment_method.delete()
        messages.success(request, f'Payment method "{name}" has been deleted successfully.')
        return redirect('dashboard:payment_method_list')
    
    context = {
        'object': payment_method,
        'object_type': 'Payment Method',
        'return_url': 'dashboard:payment_method_list',
    }
    return render(request, 'dashboard/confirm_delete.html', context)


# ============================================
# PAYMENT VERIFICATION VIEWS
# ============================================

@login_required
def payment_verification_list(request):
    """List all payment verifications (admin view)"""
    # Separate verified and unverified payments
    unverified_payments = models.PaymentVerification.objects.filter(verified=False).select_related('user', 'course', 'payment_method')
    verified_payments = models.PaymentVerification.objects.filter(verified=True).select_related('user', 'course', 'payment_method', 'verified_by')
    
    context = {
        'unverified_payments': unverified_payments,
        'verified_payments': verified_payments,
        'unverified_count': unverified_payments.count(),
        'verified_count': verified_payments.count(),
    }
    return render(request, 'dashboard/payment_verifications.html', context)


@login_required
def add_payment_verification(request):
    """Student submits payment verification request"""
    from apps.Course.forms import PaymentVerificationForm
    
    if request.method == 'POST':
        form = PaymentVerificationForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            payment_verification = form.save()
            messages.success(request, f'Payment verification request for "{payment_verification.course.title}" has been submitted successfully. Please wait for admin approval.')
            return redirect('dashboard:my_payment_verifications')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PaymentVerificationForm(user=request.user)
    
    context = {
        'form': form,
        'item_name': 'Payment Verification',
    }
    return render(request, 'dashboard/add_item.html', context)


@login_required
def payment_verification_detail(request, pk):
    """View payment verification details"""
    payment_verification = get_object_or_404(models.PaymentVerification, pk=pk)
    
    context = {
        'payment_verification': payment_verification,
        'object': payment_verification,
    }
    return render(request, 'dashboard/payment_verification_detail.html', context)


@login_required
def verify_payment(request, pk):
    """Admin verifies a payment"""
    payment_verification = get_object_or_404(models.PaymentVerification, pk=pk)
    
    if request.method == 'POST':
        notes = request.POST.get('verification_notes', '')
        action = request.POST.get('action')
        
        if action == 'approve':
            payment_verification.verify(request.user, notes)
            messages.success(request, f'Payment verified successfully. User {payment_verification.user.username} has been enrolled in {payment_verification.course.title}.')
        elif action == 'reject':
            payment_verification.verification_notes = notes
            payment_verification.save()
            messages.warning(request, 'Payment verification notes updated. Payment remains unverified.')
        
        return redirect('dashboard:payment_verification_list')
    
    context = {
        'payment_verification': payment_verification,
    }
    return render(request, 'dashboard/verify_payment.html', context)


@login_required
def my_payment_verifications(request):
    """Student views their own payment verification requests"""
    payment_verifications = models.PaymentVerification.objects.filter(user=request.user).select_related('course', 'payment_method', 'verified_by')
    
    context = {
        'payment_verifications': payment_verifications,
    }
    return render(request, 'dashboard/my_payment_verifications.html', context)


@login_required
def delete_payment_verification(request, pk):
    payment_verification = get_object_or_404(models.PaymentVerification, pk=pk)
    
    # Only allow user to delete their own unverified payments
    if payment_verification.user != request.user and not request.user.role == User.Role.ADMIN:
        messages.error(request, 'You do not have permission to delete this payment verification.')
        return redirect('dashboard:my_payment_verifications')
    
    if payment_verification.verified:
        messages.error(request, 'Cannot delete verified payment.')
        return redirect('dashboard:my_payment_verifications')
    
    if request.method == 'POST':
        course_title = payment_verification.course.title
        payment_verification.delete()
        messages.success(request, f'Payment verification for "{course_title}" has been deleted.')
        return redirect('dashboard:my_payment_verifications')
    
    context = {
        'object': payment_verification,
        'object_type': 'Payment Verification',
        'return_url': 'dashboard:my_payment_verifications',
    }
    return render(request, 'dashboard/confirm_delete.html', context)


# from django.contrib.auth.decorators import login_required
from django.db.models import Count
# from django.shortcuts import render
# from . import models


@login_required
def dashboard_view(request):
    from django.utils import timezone
    from datetime import timedelta
    
    context = {}

    # === 1. User Statistics ===
    all_users = User.objects.select_related('academic_level', 'course').all()

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
    
    # Additional user statistics
    enrolled_students = sum(1 for s in students if s.course is not None)
    active_students = sum(1 for s in students if s.is_active)
    active_teachers = sum(1 for t in teachers if t.is_active)
    
    # Recent users (last 7 days)
    week_ago = timezone.now() - timedelta(days=7)
    new_students_week = sum(1 for s in students if s.date_joined >= week_ago)
    new_teachers_week = sum(1 for t in teachers if t.date_joined >= week_ago)

    context.update({
        'total': total_users,
        'admin_count': admin_count,
        'teacher_count': teacher_count,
        'student_count': student_count,
        'teachers': teachers,
        'students': students,
        'enrolled_students': enrolled_students,
        'active_students': active_students,
        'active_teachers': active_teachers,
        'new_students_week': new_students_week,
        'new_teachers_week': new_teachers_week,
    })

    # === 2. Courses ===
    extra_activities = models.Course.objects.prefetch_related('participants').annotate(
        participant_count=Count('participants')
    ).order_by('-created_at')
    
    # Course statistics
    total_courses = extra_activities.count()
    free_courses = extra_activities.filter(cost=0).count()
    paid_courses = total_courses - free_courses
    total_enrollments = sum(course.participant_count for course in extra_activities)
    
    context.update({
        'extra_activities': extra_activities,
        'extra_activity_count': total_courses,
        'limited_activities': extra_activities[:3],
        'free_courses': free_courses,
        'paid_courses': paid_courses,
        'total_enrollments': total_enrollments,
    })

    # === 3. Academic Levels ===
    levels = models.AcademicLevel.objects.prefetch_related('subjects', 'streams').all().order_by('-pk')
    limited_levels = levels[:3]
    
    # Level statistics
    total_capacity = sum(level.capacity for level in levels if level.capacity)
    students_by_level = {}
    for level in levels:
        level_students = sum(1 for s in students if s.academic_level == level)
        students_by_level[level.id] = level_students
    
    context.update({
        'levels': levels,
        'level_count': levels.count(),
        'limited_levels': limited_levels,
        'total_capacity': total_capacity,
        'students_by_level': students_by_level,
    })

    # === 4. Subjects ===
    subjects = models.Subject.objects.select_related('levels').prefetch_related('streams').all()
    context.update({
        'subjects': subjects,
        'subject_count': subjects.count(),
        'limited_subjects': subjects[:3],
    })

    # === 5. Videos ===
    videos = models.Video.objects.select_related('subject', 'teacher', 'course', 'level').order_by('-uploaded_at')
    
    # Video statistics
    total_videos = videos.count()
    free_videos = videos.filter(cost=0).count()
    
    context.update({
        'videos': videos,
        'video_count': total_videos,
        'limited_videos': videos[:3],
        'free_videos': free_videos,
    })
    
    # === 6. Live Classes ===
    live_classes = models.LiveClass.objects.select_related('subject', 'hosts', 'level', 'course').order_by('start_time')
    now = timezone.now()
    
    # Live class statistics
    upcoming_classes = [lc for lc in live_classes if lc.start_time > now]
    live_now = [lc for lc in live_classes if lc.is_live()]
    
    context.update({
        'live_classes': live_classes,
        'live_class_count': live_classes.count(),
        'upcoming_classes': upcoming_classes[:5],
        'live_now_count': len(live_now),
    })
    
    # === 7. Streams ===
    streams = models.Stream.objects.select_related('level').annotate(
        subject_count=Count('subjects')
    ).order_by('-pk')
    
    context.update({
        'streams': streams,
        'stream_count': streams.count(),
    })
    
    # === 8. Payment Verifications ===
    payments = models.PaymentVerification.objects.select_related('user', 'course', 'payment_method').all()
    pending_payments = payments.filter(verified=False).count()
    verified_payments = payments.filter(verified=True).count()
    total_revenue = sum(p.amount for p in payments.filter(verified=True))
    
    context.update({
        'total_payments': payments.count(),
        'pending_payments': pending_payments,
        'verified_payments': verified_payments,
        'total_revenue': total_revenue,
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
    # Redirect to user detail since enrollment is now handled via user.course
    user = get_object_or_404(models.User, pk=pk)
    return redirect('dashboard:user_detail', pk=user.pk)

@login_required
def enrollment_delete(request, pk):
    # Redirect to user detail to edit course assignment
    user = get_object_or_404(models.User, pk=pk)
    if request.method == 'POST':
        # Clear the course assignment to "unenroll" the user
        user.course = None
        user.save()
        messages.success(request, f'{user.get_full_name() or user.username} has been unenrolled!')
        return redirect('dashboard:enrollment_home')
    return redirect('dashboard:user_detail', pk=pk)


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
    activity = get_object_or_404(models.Course.objects.prefetch_related('enrolled_students'), pk=pk)
    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES, instance=activity)
        
        if form.is_valid():
            form.save()
            messages.success(request, f'Activity "{activity.title}" and related videos updated successfully!')
            return redirect('dashboard:activity_detail', pk=pk)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CourseForm(instance=activity)
    
    # Get enrolled students (from User.course ForeignKey relationship)
    enrolled_students = activity.enrolled_students.all().order_by('username')
    
    context = {
        'form': form,
        'item_name': 'Activity',
        'delete_url': reverse('dashboard:activity_delete', args=[pk]),
        'object': activity,
        'enrolled_students': enrolled_students,
        'enrolled_count': enrolled_students.count()
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
    activity = get_object_or_404(models.Course, pk=pk)
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
            results['courses'] = list(models.Course.objects.filter(
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
        
        # Search Enrollments (users with courses)
        if search_all or search_type == 'enrollments':
            results['enrollments'] = list(models.User.objects.filter(
                Q(username__icontains=search_term) |
                Q(first_name__icontains=search_term) |
                Q(last_name__icontains=search_term) |
                Q(course__title__icontains=search_term),
                role=models.User.Role.STUDENT,
                course__isnull=False
            )[:20])
    
    except Exception as e:
        # Log the error and show a friendly message
        results['error'] = f"An error occurred during search: {str(e)}"
        import traceback
    
    results['search_type'] = search_type
    results['search_term'] = search_term
    
    return render(request, 'dashboard/search_results.html', results)

