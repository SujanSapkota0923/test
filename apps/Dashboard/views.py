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
    from django.db.models import Sum, Avg, Max, Min
    
    context = {}
    now = timezone.now()
    week_ago = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)

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
    unenrolled_students = student_count - enrolled_students
    active_students = sum(1 for s in students if s.is_active)
    inactive_students = student_count - active_students
    active_teachers = sum(1 for t in teachers if t.is_active)
    inactive_teachers = teacher_count - active_teachers
    
    # Recent users
    new_students_week = sum(1 for s in students if s.date_joined >= week_ago)
    new_teachers_week = sum(1 for t in teachers if t.date_joined >= week_ago)
    new_students_month = sum(1 for s in students if s.date_joined >= month_ago)
    new_teachers_month = sum(1 for t in teachers if t.date_joined >= month_ago)
    
    # Students with/without profile pictures
    students_with_photos = sum(1 for s in students if s.profile_picture)
    teachers_with_photos = sum(1 for t in teachers if t.profile_picture)
    
    # Calculate percentage of students with photos
    students_with_photos_percentage = round((students_with_photos / student_count * 100) if student_count > 0 else 0, 1)
    
    # Recent students list
    recent_students = sorted(students, key=lambda x: x.date_joined, reverse=True)[:5]
    recent_teachers = sorted(teachers, key=lambda x: x.date_joined, reverse=True)[:3]

    context.update({
        'total': total_users,
        'admin_count': admin_count,
        'teacher_count': teacher_count,
        'student_count': student_count,
        'teachers': teachers,
        'students': students,
        'enrolled_students_count': enrolled_students,
        'enrolled_students': enrolled_students,  # Keep for backward compatibility
        'unenrolled_students': unenrolled_students,
        'active_students': active_students,
        'inactive_students': inactive_students,
        'active_teachers_count': active_teachers,
        'active_teachers': active_teachers,  # Keep for backward compatibility
        'inactive_teachers': inactive_teachers,
        'new_students_week': new_students_week,
        'new_teachers_week': new_teachers_week,
        'new_students_month': new_students_month,
        'new_teachers_month': new_teachers_month,
        'students_with_photos': students_with_photos,
        'students_with_photos_percentage': students_with_photos_percentage,
        'teachers_with_photos': teachers_with_photos,
        'recent_students': recent_students,
        'recent_teachers': recent_teachers,
        'enrollment_rate': round((enrolled_students / student_count * 100) if student_count > 0 else 0, 1),
    })

    # === 2. Courses ===
    extra_activities = models.Course.objects.prefetch_related('enrolled_students').annotate(
        participant_count=Count('enrolled_students')
    ).order_by('-created_at')
    
    # Course statistics
    total_courses = extra_activities.count()
    free_courses = extra_activities.filter(cost=0).count()
    paid_courses = total_courses - free_courses
    
    # Calculate actual enrollments using enrolled_students relationship
    total_course_enrollments = sum(course.participant_count for course in extra_activities)
    
    # Course revenue statistics
    course_revenue_stats = models.Course.objects.aggregate(
        total_potential=Sum('cost'),
        avg_cost=Avg('cost'),
        max_cost=Max('cost'),
        min_paid_cost=Min('cost', filter=Q(cost__gt=0))
    )
    
    # Ongoing vs upcoming vs past courses
    ongoing_courses = [c for c in extra_activities if c.start_time <= now <= c.end_time]
    upcoming_courses = [c for c in extra_activities if c.start_time > now]
    past_courses = [c for c in extra_activities if c.end_time < now]
    
    # Popular courses (most enrolled)
    popular_courses = sorted(extra_activities, key=lambda x: x.participant_count, reverse=True)[:5]
    
    # Recent courses
    recent_courses = list(extra_activities.filter(created_at__gte=week_ago))
    
    context.update({
        'extra_activities': extra_activities,
        'extra_activity_count': total_courses,
        'limited_activities': extra_activities[:3],
        'free_courses': free_courses,
        'paid_courses': paid_courses,
        'total_enrollments': total_course_enrollments,
        'ongoing_courses_count': len(ongoing_courses),
        'upcoming_courses_count': len(upcoming_courses),
        'past_courses_count': len(past_courses),
        'popular_courses': popular_courses,
        'recent_courses_count': len(recent_courses),
        'avg_course_cost': round(course_revenue_stats['avg_cost'] or 0, 2),
        'max_course_cost': course_revenue_stats['max_cost'] or 0,
    })

    # === 3. Academic Levels ===
    levels = models.AcademicLevel.objects.prefetch_related('subjects', 'streams').all().order_by('order')
    limited_levels = levels[:3]
    
    # Level statistics
    total_capacity = sum(level.capacity for level in levels if level.capacity)
    students_by_level = {}
    level_details = []
    
    for level in levels:
        level_students = sum(1 for s in students if s.academic_level == level)
        students_by_level[level.id] = level_students
        
        # Level utilization
        if level.capacity:
            utilization = round((level_students / level.capacity * 100), 1)
        else:
            utilization = 0
            
        level_details.append({
            'level': level,
            'student_count': level_students,
            'utilization': utilization,
            'subject_count': level.subjects.count(),
            'stream_count': level.streams.count() if level.allows_streams else 0,
        })
    
    # Most populated levels
    most_populated_levels = sorted(level_details, key=lambda x: x['student_count'], reverse=True)[:3]
    levels_with_streams = sum(1 for l in levels if l.allows_streams)
    
    context.update({
        'levels': levels,
        'level_count': levels.count(),
        'limited_levels': limited_levels,
        'total_capacity': total_capacity,
        'students_by_level': students_by_level,
        'level_details': level_details,
        'most_populated_levels': most_populated_levels,
        'levels_with_streams': levels_with_streams,
        'capacity_utilization': round((student_count / total_capacity * 100) if total_capacity > 0 else 0, 1),
    })

    # === 4. Subjects ===
    subjects = models.Subject.objects.select_related('levels').prefetch_related('streams').all()
    
    # Subject statistics
    subjects_with_videos = models.Subject.objects.annotate(
        video_count=Count('videos')
    ).filter(video_count__gt=0).count()
    
    subjects_with_classes = models.Subject.objects.annotate(
        class_count=Count('live_classes')
    ).filter(class_count__gt=0).count()
    
    # Subjects by level distribution
    subjects_by_level_count = {}
    for level in levels:
        subjects_by_level_count[level.name] = subjects.filter(levels=level).count()
    
    context.update({
        'subjects': subjects,
        'subject_count': subjects.count(),
        'limited_subjects': subjects[:3],
        'subjects_with_videos': subjects_with_videos,
        'subjects_with_classes': subjects_with_classes,
        'subjects_by_level_count': subjects_by_level_count,
    })

    # === 5. Videos ===
    videos = models.Video.objects.select_related('subject', 'teacher', 'course', 'level').order_by('-uploaded_at')
    
    # Video statistics
    total_videos = videos.count()
    free_videos_count = videos.filter(cost=0).count()
    paid_videos = total_videos - free_videos_count
    
    # Video revenue statistics
    video_revenue_stats = videos.aggregate(
        total_potential=Sum('cost'),
        avg_cost=Avg('cost')
    )
    
    # === 6. Live Classes ===
    live_classes = models.LiveClass.objects.select_related('subject', 'hosts', 'level', 'course').order_by('start_time')
    
    # Live class statistics
    all_classes_list = list(live_classes)
    upcoming_classes = [lc for lc in all_classes_list if lc.start_time > now]
    past_classes = [lc for lc in all_classes_list if lc.end_time < now]
    live_now = [lc for lc in all_classes_list if lc.is_live()]
    recorded_classes = [lc for lc in all_classes_list if lc.is_recorded]
    
    # Classes this week/month
    classes_this_week = [lc for lc in all_classes_list if week_ago <= lc.start_time <= now]
    classes_this_month = [lc for lc in all_classes_list if month_ago <= lc.start_time <= now]
    
    # Classes by teacher (top hosts)
    classes_by_teacher = {}
    for lc in all_classes_list:
        if lc.hosts:
            teacher_name = lc.hosts.get_full_name() or lc.hosts.username
            classes_by_teacher[teacher_name] = classes_by_teacher.get(teacher_name, 0) + 1
    
    top_class_hosts = sorted(classes_by_teacher.items(), key=lambda x: x[1], reverse=True)[:5]
    
    context.update({
        'live_classes': live_classes,
        'live_class_count': live_classes.count(),
        'upcoming_classes': upcoming_classes[:5],
        'upcoming_classes_count': len(upcoming_classes),
        'live_now_count': len(live_now),
        'live_now': live_now,
        'past_classes_count': len(past_classes),
        'recorded_classes_count': len(recorded_classes),
        'classes_this_week_count': len(classes_this_week),
        'classes_this_month_count': len(classes_this_month),
        'top_class_hosts': top_class_hosts,
    })
    
    # Recent videos
    recent_videos = list(videos.filter(uploaded_at__gte=week_ago))
    videos_this_month = list(videos.filter(uploaded_at__gte=month_ago))
    
    # Videos by teacher (top contributors)
    video_by_teacher = {}
    for video in videos:
        if video.teacher:
            teacher_name = video.teacher.get_full_name() or video.teacher.username
            video_by_teacher[teacher_name] = video_by_teacher.get(teacher_name, 0) + 1
    
    top_video_contributors = sorted(video_by_teacher.items(), key=lambda x: x[1], reverse=True)[:5]
    
    context.update({
        'videos': videos,
        'video_count': total_videos,
        'limited_videos': videos[:3],
        'free_videos_count': free_videos_count,
        'free_videos': free_videos_count,  # Keep for backward compatibility
        'paid_videos': paid_videos,
        'recent_videos_count': len(recent_videos),
        'videos_this_month_count': len(videos_this_month),
        'avg_video_cost': round(video_revenue_stats['avg_cost'] or 0, 2),
        'top_video_contributors': top_video_contributors,
    })

    # === 7. Streams ===
    streams = models.Stream.objects.select_related('level').annotate(
        subject_count=Count('subjects')
    ).order_by('-pk')
    
    context.update({
        'streams': streams,
        'stream_count': streams.count(),
    })
    
    # === 8. Payment Methods ===
    payment_methods = models.PaymentMethod.objects.all()
    active_payment_methods = payment_methods.filter(is_active=True).count()
    
    context.update({
        'payment_methods_count': payment_methods.count(),
        'active_payment_methods': active_payment_methods,
    })
    
    # === 9. Payment Verifications ===
    payments = models.PaymentVerification.objects.select_related('user', 'course', 'payment_method', 'verified_by').all()
    all_payments_list = list(payments)
    
    pending_payments = [p for p in all_payments_list if not p.verified]
    verified_payments = [p for p in all_payments_list if p.verified]
    
    # Revenue statistics
    total_revenue = sum(p.amount for p in verified_payments)
    pending_revenue = sum(p.amount for p in pending_payments)
    
    # Recent payments
    recent_payments = sorted(all_payments_list, key=lambda x: x.created_at, reverse=True)[:5]
    payments_this_week = [p for p in all_payments_list if p.created_at >= week_ago]
    payments_this_month = [p for p in all_payments_list if p.created_at >= month_ago]
    
    # Payment method distribution
    payments_by_method = {}
    for p in verified_payments:
        method_name = p.payment_method.name
        payments_by_method[method_name] = payments_by_method.get(method_name, 0) + 1
    
    most_used_payment_methods = sorted(payments_by_method.items(), key=lambda x: x[1], reverse=True)[:3]
    
    # Average payment amount
    avg_payment = round(total_revenue / len(verified_payments), 2) if verified_payments else 0
    
    context.update({
        'total_payments': payments.count(),
        'pending_payments_count': len(pending_payments),
        'verified_payments_count': len(verified_payments),
        'total_revenue': round(total_revenue, 2),
        'pending_revenue': round(pending_revenue, 2),
        'recent_payments': recent_payments,
        'payments_this_week_count': len(payments_this_week),
        'payments_this_month_count': len(payments_this_month),
        'most_used_payment_methods': most_used_payment_methods,
        'avg_payment': avg_payment,
        'verification_rate': round((len(verified_payments) / len(all_payments_list) * 100) if all_payments_list else 0, 1),
    })
    
    # === 10. Overall System Health ===
    total_content_items = total_courses + total_videos + live_classes.count()
    total_academic_resources = subjects.count() + levels.count() + streams.count()
    data_completeness = round((
        (students_with_photos + teachers_with_photos) / (student_count + teacher_count) * 100
    ) if (student_count + teacher_count) > 0 else 0, 1)
    
    context.update({
        'total_content_items': total_content_items,
        'total_users': total_users,
        'total_academic_resources': total_academic_resources,
        'data_completeness': data_completeness,
        'system_health': {
            'total_content_items': total_content_items,
            'total_users': total_users,
            'total_academic_resources': total_academic_resources,
            'data_completeness': data_completeness,
        }
    })

    return render(request, 'dashboard/index.html', context)








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



@login_required
def level_delete(request, pk):
    level = get_object_or_404(models.AcademicLevel, pk=pk)
    if request.method == 'POST':
        name = level.name
        level.delete()
        messages.success(request, f'Level "{name}" deleted successfully!')
        return redirect('dashboard:index')
    return redirect('dashboard:level_detail', pk=pk)




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




@login_required
def stream_delete(request, pk):
    stream = get_object_or_404(models.Stream, pk=pk)
    if request.method == 'POST':
        name = stream.name
        stream.delete()
        messages.success(request, f'Stream "{name}" deleted successfully!')
        return redirect('dashboard:stream_home')
    return redirect('dashboard:stream_detail', pk=pk)




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




@login_required
def subject_delete(request, pk):
    subject = get_object_or_404(models.Subject, pk=pk)
    if request.method == 'POST':
        name = subject.name
        subject.delete()
        messages.success(request, f'Subject "{name}" deleted successfully!')
        return redirect('dashboard:subject_home')
    return redirect('dashboard:subject_detail', pk=pk)




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



@login_required
def liveclass_delete(request, pk):
    live_class = get_object_or_404(models.LiveClass, pk=pk)
    if request.method == 'POST':
        title = live_class.title
        live_class.delete()
        messages.success(request, f'Live Class "{title}" deleted successfully!')
        return redirect('dashboard:live_classes')
    return redirect('dashboard:liveclass_detail', pk=pk)



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



@login_required
def activity_delete(request, pk):
    activity = get_object_or_404(models.Course, pk=pk)
    if request.method == 'POST':
        title = activity.title
        activity.delete()
        messages.success(request, f'Activity "{title}" deleted successfully!')
        return redirect('dashboard:course_home')
    return redirect('dashboard:activity_detail', pk=pk)


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
        'payment_methods': [],
        'payment_verifications': [],
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
        'payment': 'payment_methods',
        'payments': 'payment_methods',
        'method': 'payment_methods',
        'verification': 'payment_verifications',
        'verifications': 'payment_verifications',
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
        
        # Search Payment Methods
        if search_all or search_type == 'payment_methods':
            results['payment_methods'] = list(models.PaymentMethod.objects.filter(
                Q(name__icontains=search_term) |
                Q(description__icontains=search_term)
            )[:20])
        
        # Search Payment Verifications
        if search_all or search_type == 'payment_verifications':
            results['payment_verifications'] = list(models.PaymentVerification.objects.filter(
                Q(user__username__icontains=search_term) |
                Q(user__first_name__icontains=search_term) |
                Q(user__last_name__icontains=search_term) |
                Q(course__title__icontains=search_term) |
                Q(payment_method__name__icontains=search_term) |
                Q(transaction_id__icontains=search_term) |
                Q(remarks__icontains=search_term) |
                Q(verification_notes__icontains=search_term)
            ).select_related('user', 'course', 'payment_method', 'verified_by')[:20])
    
    except Exception as e:
        # Log the error and show a friendly message
        results['error'] = f"An error occurred during search: {str(e)}"
        import traceback
    
    results['search_type'] = search_type
    results['search_term'] = search_term
    
    return render(request, 'dashboard/search_results.html', results)

