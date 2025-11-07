
from django import forms
from .models import User, AcademicLevel, Stream, Subject, Enrollment, LiveClass, ExtraCurricularActivity, Video

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
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter stream name (e.g., Science)'}),
            'slug': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter slug (e.g., science)'}),
            'level': forms.Select(attrs={'class': 'form-select'}),
        }


class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['name', 'description', 'levels', 'streams']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter subject name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter description'}),
            'levels': forms.Select(attrs={'class': 'form-select'}),
            'streams': forms.SelectMultiple(attrs={'class': 'form-select', 'size': '5'}),
        }


class EnrollmentForm(forms.Form):
    """Form to assign academic level to a student (updates User.academic_level)"""
    student = forms.ModelChoiceField(
        queryset=User.objects.filter(role=User.Role.STUDENT, academic_level__isnull=True),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Student',
        help_text='Select a student without an assigned academic level'
    )
    level = forms.ModelChoiceField(
        queryset=AcademicLevel.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Academic Level',
        help_text='Select the academic level to assign to this student'
    )

    def save(self):
        """Update the user's academic_level field"""
        student = self.cleaned_data['student']
        level = self.cleaned_data['level']
        student.academic_level = level
        student.save()
        return student


class EnrollmentEditForm(forms.Form):
    """Form to edit an existing student's academic level (student field is read-only)"""
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
        label='Academic Level',
        help_text='Select the new academic level for this student'
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
    class Meta:
        model = Enrollment
        fields = ['student', 'level', 'is_active']
        widgets = {
            'student': forms.Select(attrs={'class': 'form-select'}),
            'level': forms.Select(attrs={'class': 'form-select'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show students who don't have active enrollments (for new enrollments)
        if not self.instance.pk:
            enrolled_student_ids = Enrollment.objects.filter(
                is_active=True
            ).values_list('student_id', flat=True)
            
            self.fields['student'].queryset = User.objects.filter(
                role=User.Role.STUDENT
            ).exclude(id__in=enrolled_student_ids)

            
class LiveClassForm(forms.ModelForm):
    class Meta:
        model = LiveClass
        fields = ['title', 'level', 'subject', 'hosts', 'start_time', 'end_time', 'meeting_url', 'description', 'is_recorded', 'recording_url']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter class title'}),
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


class ExtraCurricularActivityForm(forms.ModelForm):
    class Meta:
        model = ExtraCurricularActivity
        fields = ['title', 'description', 'participants', 'start_time', 'end_time', 'image']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter activity title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter description'}),
            'participants': forms.SelectMultiple(attrs={'class': 'form-select', 'size': '5'}),
            'start_time': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'end_time': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

class VideoUploadForm(forms.ModelForm):
    class Meta:
        model = Video
        fields = ['title', 'description', 'url', 'course', 'level', 'subject', 'stream','teacher','cost', 'image']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter video title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter description'}),
            'url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Enter video URL'}),
            'course': forms.Select(attrs={'class': 'form-select', 'placeholder': 'Select extra-curricular activity (if applicable)'}),
            'level': forms.Select(attrs={'class': 'form-select', 'placeholder': 'Select academic level'}),
            'subject': forms.Select(attrs={'class': 'form-select', 'placeholder': 'Select subject'}),
            'stream': forms.SelectMultiple(attrs={'class': 'form-select', 'placeholder': 'Select stream (if applicable)'}),
            'teacher': forms.Select(attrs={'class': 'form-select', 'placeholder': 'Select teacher'}),
            'cost': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter cost (Blank for free)'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }