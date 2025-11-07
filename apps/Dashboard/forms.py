
# This form is for the Course Management System application.
# this form will be shown when previous object are needed to be edited.




from django import forms
from apps.Course.models import User
from django.contrib.auth.forms import UserCreationForm
from django.forms import inlineformset_factory  

class UserSignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2', 'role', 'phone', 'profile_picture', 'first_name', 'last_name']
        # widgets = {
        #     'bio': forms.Textarea(attrs={'rows': 3}),
        # }

class UserLoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))


from apps.Course.models import AcademicLevel, Stream, Subject, Enrollment, LiveClass, ExtraCurricularActivity, Video, User

# ============================================
# USER FORMS
# ============================================
class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'role', 'phone', 
                  'bio', 'profile_picture', 'academic_level']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-select'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+977-9876543210'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'academic_level': forms.Select(attrs={'class': 'form-select'}),
        }
        help_texts = {
            'username': 'Required. 150 characters or fewer.',
            'role': 'Select user role (Student requires academic level)',
            'academic_level': 'Required only for students'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make academic_level required only for students
        self.fields['academic_level'].required = False


class UserCreateForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 
                  'password2', 'role', 'phone', 'profile_picture', 'academic_level']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-select'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'academic_level': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})


# ============================================
# ACADEMIC LEVEL FORM
# ============================================
class AcademicLevelForm(forms.ModelForm):
    class Meta:
        model = AcademicLevel
        fields = ['name', 'slug', 'order', 'allows_streams', 'capacity']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Grade 10'}),
            'slug': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., grade-10'}),
            'order': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'allows_streams': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'capacity': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        }
        help_texts = {
            'slug': 'URL-friendly identifier (use hyphens)',
            'order': 'Lower numbers appear first',
            'allows_streams': 'Check if this level has streams (Science, Management, etc.)',
            'capacity': 'Maximum students (leave empty for unlimited)'
        }


# ============================================
# STREAM FORM
# ============================================
class StreamForm(forms.ModelForm):
    class Meta:
        model = Stream
        fields = ['name', 'slug', 'level']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Science'}),
            'slug': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., science'}),
            'level': forms.Select(attrs={'class': 'form-select'}),
        }
        help_texts = {
            'level': 'Select an academic level that allows streams'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter to only show levels that allow streams
        self.fields['level'].queryset = AcademicLevel.objects.filter(allows_streams=True)
    

# ============================================
# SUBJECT FORM
# ============================================
class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['name', 'description', 'levels', 'streams']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Mathematics'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'levels': forms.Select(attrs={'class': 'form-select'}),
            'streams': forms.SelectMultiple(attrs={'class': 'form-select', 'size': '5'}),
        }
        help_texts = {
            'streams': 'Hold Ctrl/Cmd to select multiple streams (optional)'
        }


# ============================================
# ENROLLMENT FORM
# ============================================
class EnrollmentForm(forms.ModelForm):
    class Meta:
        model = Enrollment
        fields = ['student', 'level', 'joined_at', 'is_active']
        widgets = {
            'student': forms.Select(attrs={'class': 'form-select'}),
            'level': forms.Select(attrs={'class': 'form-select'}),
            'joined_at': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show students
        self.fields['student'].queryset = User.objects.filter(role=User.Role.STUDENT)


# ============================================
# LIVE CLASS FORM
# ============================================
class LiveClassForm(forms.ModelForm):
    class Meta:
        model = LiveClass
        fields = ['title', 'level', 'subject', 'hosts', 'start_time', 'end_time', 
                  'meeting_url', 'description', 'is_recorded', 'recording_url']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Introduction to Calculus'}),
            'level': forms.Select(attrs={'class': 'form-select'}),
            'subject': forms.Select(attrs={'class': 'form-select'}),
            'hosts': forms.Select(attrs={'class': 'form-select'}),
            'start_time': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'end_time': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'meeting_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://zoom.us/j/...'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_recorded': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'recording_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://...'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show teachers as hosts
        self.fields['hosts'].queryset = User.objects.filter(role=User.Role.TEACHER)


# ============================================
# EXTRA CURRICULAR ACTIVITY FORM
# ============================================

from django.forms import inlineformset_factory
from apps.Course import models
class ExtraCurricularActivityForm(forms.ModelForm):
    # Field to select existing videos to associate with this activity
    videos = forms.ModelMultipleChoiceField(
        queryset=models.Video.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={
            'class': 'form-select',
            'size': '10',
            'style': 'min-height: 200px;'
        }),
        help_text='Hold Ctrl/Cmd to select multiple videos. Selected videos will be linked to this course.'
    )
    
    class Meta:
        model = ExtraCurricularActivity
        fields = ['title', 'description', 'cost', 'start_time', 'end_time', 'image', 'participants']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Annual Sports Day'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'cost': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter cost (0 for free)'}),
            'start_time': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'end_time': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'image': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'participants': forms.SelectMultiple(attrs={'class': 'form-select', 'size': '8'}),
        }
        help_texts = {
            'participants': 'Hold Ctrl/Cmd to select multiple participants (optional)'
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # If editing an existing activity, pre-select its videos
        if self.instance and self.instance.pk:
            self.fields['videos'].initial = self.instance.videos.all()
    
    def save(self, commit=True):
        instance = super().save(commit=commit)
        if commit:
            # Update the videos associated with this activity
            instance.videos.set(self.cleaned_data['videos'])
        return instance

# ============================================
# VIDEO FORM
# ============================================
class VideoForm(forms.ModelForm):
    class Meta:
        model = Video
        fields = ['title', 'description', 'url', 'level','course', 'subject', 'stream', 
                  'teacher', 'cost', 'image']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Algebra Basics'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://youtube.com/...'}),
            'level': forms.Select(attrs={'class': 'form-select'}),
            'course': forms.Select(attrs={'class': 'form-select'}),
            'subject': forms.Select(attrs={'class': 'form-select'}),
            'stream': forms.SelectMultiple(attrs={'class': 'form-select', 'size': '5'}),
            'teacher': forms.Select(attrs={'class': 'form-select'}),
            'cost': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'step': '0.01'}),
            'image': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        }
        help_texts = {
            'cost': 'Enter 0 for free videos',
            'stream': 'Hold Ctrl/Cmd to select multiple streams (optional)'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show teachers
        self.fields['teacher'].queryset = User.objects.filter(role=User.Role.TEACHER)


# ============================================
# VIDEO INLINE FORMSET FOR ACTIVITY
# ============================================
VideoFormSet = inlineformset_factory(
    ExtraCurricularActivity,
    Video,
    fields=['title', 'description', 'url', 'course', 'level', 'subject', 'stream', 'teacher', 'cost', 'image'],
    extra=1,
    can_delete=True,
    widgets={
        'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Video title'}),
        'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Brief description'}),
        'url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://youtube.com/...'}),
        'course': forms.Select(attrs={'class': 'form-select'}),
        'level': forms.Select(attrs={'class': 'form-select'}),
        'subject': forms.Select(attrs={'class': 'form-select'}),
        'stream': forms.SelectMultiple(attrs={'class': 'form-select', 'size': '3'}),
        'teacher': forms.Select(attrs={'class': 'form-select'}),
        'cost': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'step': '0.01', 'placeholder': '0.00'}),
        'image': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
    }
)

