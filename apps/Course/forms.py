
from django import forms
from .models import User, AcademicLevel, Stream, Subject, Enrollment, LiveClass, Course, Video

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter password'
    }))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Confirm password'
    }))
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'phone', 'role', 'academic_level', 'bio', 'profile_picture']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter username'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter first name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter last name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter email'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter phone number'}),
            'role': forms.Select(attrs={'class': 'form-select'}),
            'academic_level': forms.Select(attrs={'class': 'form-select'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter bio'}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match")
        
        return cleaned_data
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class AcademicLevelForm(forms.ModelForm):
    class Meta:
        model = AcademicLevel
        fields = ['name', 'slug', 'order', 'allows_streams', 'capacity']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter level name (e.g., Grade 10)'}),
            'slug': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter slug (e.g., grade-10)'}),
            'order': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter order number'}),
            'allows_streams': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'capacity': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter capacity (optional)'}),
        }


class StreamForm(forms.ModelForm):
    class Meta:
        model = Stream
        fields = ['name', 'slug', 'level']
        labels = {
            'level': 'Class', 
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter stream name (e.g., Science)'}),
            'slug': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter slug (e.g., science)'}),
            'level': forms.Select(attrs={'class': 'form-select'}),
        }


class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['name', 'description', 'levels', 'streams']
        labels = {
            'levels': 'Class', 
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter subject name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter description'}),
            'levels': forms.Select(attrs={'class': 'form-select'}),
            'streams': forms.SelectMultiple(attrs={'class': 'form-select', 'size': '5'}),
        }


class EnrollmentForm(forms.Form):
    """Form to enroll a student into a Course (level optional)"""
    student = forms.ModelChoiceField(
        queryset=User.objects.filter(role=User.Role.STUDENT),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Student',
        help_text='Select a student to enroll'
    )
    course = forms.ModelChoiceField(
        queryset=Course.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Course',
        help_text='Select the course/activity to enroll the student into'
    )
    level = forms.ModelChoiceField(
        queryset=AcademicLevel.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Class',
        required=False,
        help_text='Optional: select a class for this enrollment'
    )

    def save(self):
        """Create an Enrollment for the selected student and course/level"""
        student = self.cleaned_data['student']
        course = self.cleaned_data['course']
        level = self.cleaned_data.get('level')
        # create active enrollment; let model validation handle conflicts
        enrollment = Enrollment.objects.create(student=student, course=course, level=level, is_active=True)
        return enrollment


class EnrollmentEditForm(forms.Form):
    """Form to edit an existing student's class (student field is read-only)"""
    student = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'readonly': 'readonly'
        }),
        label='Student',
        help_text='Student cannot be changed',
        required=False
    )
    level = forms.ModelChoiceField(
        queryset=AcademicLevel.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'}),
    label='Class',
    help_text='Select the new class for this student'
    )
    
    def __init__(self, *args, user_instance=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user_instance:
            # Set the student field to display the user's full name
            student_name = user_instance.get_full_name() or user_instance.username
            self.fields['student'].initial = student_name
            # Set the current academic level
            if user_instance.academic_level:
                self.fields['level'].initial = user_instance.academic_level
            self.user_instance = user_instance
        
        # Make student field read-only by preventing it from being changed
        self.fields['student'].widget.attrs['readonly'] = 'readonly'
        self.fields['student'].widget.attrs['style'] = 'background-color: #e9ecef; cursor: not-allowed;'
    
    def save(self):
        """Update the user's academic_level field"""
        level = self.cleaned_data['level']
        self.user_instance.academic_level = level
        self.user_instance.save()
        return self.user_instance


class EnrollmentModelForm(forms.ModelForm):
    """Original enrollment form (kept for backward compatibility if needed)"""
    labels = {
            'level': 'Class', 
        }
    class Meta:
        model = Enrollment
        fields = ['student', 'course', 'level', 'is_active']
        
        widgets = {
            'student': forms.Select(attrs={'class': 'form-select'}),
            'level': forms.Select(attrs={'class': 'form-select'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # If editing an existing enrollment, make the student field read-only so it cannot be changed here
        if self.instance and getattr(self.instance, 'pk', None):
            # disable changing student on edit
            if 'student' in self.fields:
                self.fields['student'].disabled = True
                self.fields['student'].widget.attrs.update({'readonly': 'readonly', 'style': 'background-color: #e9ecef; cursor: not-allowed;'})

        # For backward compatibility we do not prevent selecting students who have other active enrollments
        # when creating new enrollments, because course-based enrollments are allowed to be multiple. If you
        # want to restrict this list, customize the filtering here.

            
class LiveClassForm(forms.ModelForm):
    class Meta:
        model = LiveClass
        fields = ['title', 'course' ,'level', 'subject', 'hosts', 'start_time', 'end_time', 'meeting_url', 'description', 'is_recorded', 'recording_url']
        labels = {
            'level': 'Class', 
        }
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter class title'}),
            'course': forms.Select(attrs={'class': 'form-select'}),
            'level': forms.Select(attrs={'class': 'form-select'}),
            'subject': forms.Select(attrs={'class': 'form-select'}),
            'hosts': forms.Select(attrs={'class': 'form-select'}),
            'start_time': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'end_time': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'meeting_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Enter meeting URL'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter description'}),
            'is_recorded': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'recording_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Enter recording URL (optional)'}),
        }


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'description', 'participants', 'start_time', 'end_time', 'image']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter course title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter description'}),
            'participants': forms.SelectMultiple(attrs={'class': 'form-select', 'size': '5'}),
            'start_time': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'end_time': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

class VideoUploadForm(forms.ModelForm):
    labels = {
            'level': 'Class', 
        }
    class Meta:
        model = Video
        fields = ['title', 'description', 'url', 'course', 'level', 'subject', 'stream','teacher','cost', 'image']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter video title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter description'}),
            'url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Enter video URL'}),
            'course': forms.Select(attrs={'class': 'form-select', 'placeholder': 'Select extra-curricular activity (if applicable)'}),
            'level': forms.Select(attrs={'class': 'form-select', 'placeholder': 'Select class'}),
            'subject': forms.Select(attrs={'class': 'form-select', 'placeholder': 'Select subject'}),
            'stream': forms.SelectMultiple(attrs={'class': 'form-select', 'placeholder': 'Select stream (if applicable)'}),
            'teacher': forms.Select(attrs={'class': 'form-select', 'placeholder': 'Select teacher'}),
            'cost': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter cost (Blank for free)'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }