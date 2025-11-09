from django.shortcuts import render

# Create your views here.

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import User, AcademicLevel, Stream, Subject, Enrollment, LiveClass, Course
from .forms import (UserForm, AcademicLevelForm, StreamForm, SubjectForm, 
                    EnrollmentForm, LiveClassForm, CourseForm, VideoUploadForm)


# Generic Add View
@login_required
def add_user(request):
    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'User added successfully!')
            return redirect('dashboard:index') 
    else:
        form = UserForm()
    
    context = {
        'form': form,
        'item_name': 'User',
        'back_url': 'user_list',  
    }
    return render(request, 'dashboard/add_item.html', context)  


@login_required
def add_academic_level(request):
    if request.method == 'POST':
        form = AcademicLevelForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Class added successfully!')
            return redirect('dashboard:index')
    else:
        form = AcademicLevelForm()
    
    context = {
        'form': form,
        'item_name': 'Class',
        'back_url': 'academic_level_list',
    }
    return render(request, 'dashboard/add_item.html', context)




@login_required
def add_stream(request):
    if request.method == 'POST':
        form = StreamForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Stream added successfully!')
            return redirect('dashboard:stream_home')
    else:
        form = StreamForm()
    
    context = {
        'form': form,
        'item_name': 'Stream',
        'back_url': 'stream_list',
    }
    return render(request, 'dashboard/add_item.html', context)


@login_required
def add_subject(request):
    if request.method == 'POST':
        form = SubjectForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Subject added successfully!')
            return redirect('subject_list')
    else:
        form = SubjectForm()
    
    context = {
        'form': form,
        'item_name': 'Subject',
        'back_url': 'subject_list',
    }
    return render(request, 'dashboard/add_item.html', context)


@login_required
def add_enrollment(request):
    if request.method == 'POST':
        form = EnrollmentForm(request.POST)
        # if a course is selected, exclude students already active in that course
        course_id = request.POST.get('course')
        if course_id:
            enrolled_student_ids = Enrollment.objects.filter(course_id=course_id, is_active=True).values_list('student_id', flat=True)
            form.fields['student'].queryset = User.objects.filter(role=User.Role.STUDENT).exclude(id__in=enrolled_student_ids)

        if form.is_valid():
            try:
                enrollment = form.save()
            except Exception as exc:
                # Model validation (capacity/duplicate) bubbled up; show friendly error
                from django.core.exceptions import ValidationError
                if isinstance(exc, ValidationError):
                    form.add_error(None, exc.message_dict if hasattr(exc, 'message_dict') else exc.messages)
                    messages.error(request, f"Could not create enrollment: {exc}")
                else:
                    messages.error(request, f"Could not create enrollment: {exc}")
                return render(request, 'dashboard/add_item.html', {'form': form, 'item_name': 'Student Class', 'back_url': 'enrollment_list'})

            student = enrollment.student
            messages.success(request, f'Enrollment created for {student.username} successfully!')
            return redirect('dashboard:enrollment_home')
    else:
        form = EnrollmentForm()
    
    context = {
        'form': form,
        'item_name': 'Student Class',
        'back_url': 'enrollment_list',
    }
    return render(request, 'dashboard/add_item.html', context)


@login_required
def add_live_class(request):
    if request.method == 'POST':
        form = LiveClassForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Live Class added successfully!')
            return redirect('dashboard:live_classes')
    else:
        form = LiveClassForm()
    
    context = {
        'form': form,
        'item_name': 'Live Class',
        'back_url': 'live_class_list',
    }
    return render(request, 'dashboard/add_item.html', context)


@login_required
def add_activity(request):
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Activity added successfully!')
            return redirect('dashboard:course_home')
    else:
        form = CourseForm()
    
    context = {
        'form': form,
        'item_name': 'Courses',
        'back_url': 'activity_list',
    }
    return render(request, 'dashboard/add_item.html', context)


@login_required
def add_video(request):
    if request.method == 'POST':
        form = VideoUploadForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Video uploaded successfully!')
            return redirect('dashboard:video_home')
    else:
        form = VideoUploadForm()
    
    context = {
        'form': form,
        'item_name': 'Video',
        'back_url': 'video_list',
    }
    return render(request, 'dashboard/add_item.html', context)

# List View Example (for subjects)
@login_required
def subject_list(request):
    subjects = Subject.objects.all()
    context = {
        'subjects': subjects,
    }
    return render(request, 'dashboard/subjects.html', context)