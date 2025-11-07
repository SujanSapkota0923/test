from django.shortcuts import render

# Create your views here.

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import User, AcademicLevel, Stream, Subject, Enrollment, LiveClass, ExtraCurricularActivity
from .forms import (UserForm, AcademicLevelForm, StreamForm, SubjectForm, 
                    EnrollmentForm, LiveClassForm, ExtraCurricularActivityForm, VideoUploadForm)


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
            messages.success(request, 'Academic Level added successfully!')
            return redirect('dashboard:index')
    else:
        form = AcademicLevelForm()
    
    context = {
        'form': form,
        'item_name': 'Academic Level',
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
        if form.is_valid():
            student = form.save()
            messages.success(request, f'Academic level assigned to {student.username} successfully!')
            return redirect('dashboard:enrollment_home')
    else:
        form = EnrollmentForm()
    
    context = {
        'form': form,
        'item_name': 'Student Academic Level',
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
        form = ExtraCurricularActivityForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Activity added successfully!')
            return redirect('dashboard:course_home')
    else:
        form = ExtraCurricularActivityForm()
    
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