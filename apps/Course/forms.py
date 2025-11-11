
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.forms import inlineformset_factory
from .models import User, AcademicLevel, Stream, Subject, LiveClass, Course, Video, PaymentMethod, PaymentVerification

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
        fields = ['username', 'first_name', 'last_name', 'email', 'phone', 'role', 'academic_level', 'course', 'bio', 'profile_picture']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter username'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter first name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter last name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter email'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter phone number'}),
            'role': forms.Select(attrs={'class': 'form-select'}),
            'academic_level': forms.Select(attrs={'class': 'form-select'}),
            'course': forms.Select(attrs={'class': 'form-select'}),
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
    """Form to enroll a student into a Course"""
    student = forms.ModelChoiceField(
        queryset=User.objects.filter(role=User.Role.STUDENT, course__isnull=True),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Student',
        help_text='Select a student to enroll (only students not already enrolled)'
    )
    course = forms.ModelChoiceField(
        queryset=Course.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Course',
        help_text='Select the course to enroll the student into'
    )

    def save(self):
        """Assign course to student"""
        student = self.cleaned_data['student']
        course = self.cleaned_data['course']
        student.course = course
        student.save()
        return student

            
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


class PaymentMethodForm(forms.ModelForm):
    class Meta:
        model = PaymentMethod
        fields = ['name', 'description', 'details', 'image', 'is_active', 'display_order']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Enter payment method name (e.g., Bank Transfer, Khalti, eSewa)'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3, 
                'placeholder': 'Enter description and instructions'
            }),
            'details': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 4,
                'placeholder': 'Enter JSON details (e.g., {"account_number": "12345", "account_name": "School Name"})'
            }),
            'image': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'display_order': forms.NumberInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Enter display order (lower numbers appear first)'
            }),
        }
        help_texts = {
            'details': 'Optional JSON data for account info, QR codes, etc.',
            'display_order': 'Payment methods are sorted by this order',
        }
    
    def clean_details(self):
        """Validate JSON field"""
        import json
        details = self.cleaned_data.get('details')
        if details:
            try:
                if isinstance(details, str):
                    json.loads(details)
            except json.JSONDecodeError:
                raise forms.ValidationError('Invalid JSON format. Please use valid JSON syntax.')
        return details


class PaymentVerificationForm(forms.ModelForm):
    class Meta:
        model = PaymentVerification
        fields = ['course', 'payment_method', 'amount', 'transaction_id', 'payment_proof', 'remarks']
        widgets = {
            'course': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'payment_method': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '0.01',
                'placeholder': 'Enter amount paid'
            }),
            'transaction_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter transaction ID or reference number (optional)'
            }),
            'payment_proof': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'remarks': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Add any additional notes about your payment...'
            }),
        }
        help_texts = {
            'course': 'Select the course you want to purchase',
            'payment_method': 'Select the payment method you used',
            'amount': 'Enter the exact amount you paid',
            'transaction_id': 'Optional: Your transaction ID from the payment provider',
            'payment_proof': 'Upload a screenshot or photo of your payment receipt',
            'remarks': 'Optional: Any additional information about the payment',
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        # Only show active payment methods
        self.fields['payment_method'].queryset = PaymentMethod.objects.filter(is_active=True)
        # Only show courses the user hasn't enrolled in
        if self.user:
            self.fields['course'].queryset = Course.objects.exclude(enrolled_students=self.user)
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.user:
            instance.user = self.user
        if commit:
            instance.save()
        return instance


class PaymentVerificationAdminForm(forms.ModelForm):
    """Form for admin to verify payments"""
    class Meta:
        model = PaymentVerification
        fields = ['verification_notes', 'verified']
        widgets = {
            'verification_notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Add verification notes...'
            }),
            'verified': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        labels = {
            'verification_notes': 'Admin Notes',
            'verified': 'Approve Payment',
        }
        help_texts = {
            'verification_notes': 'Add any notes about the verification process',
            'verified': 'Check this box to approve the payment and enroll the user in the course',
        }


# ==========================
# Dashboard / compatibility forms
# ==========================


class UserSignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2', 'role', 'phone', 'profile_picture', 'first_name', 'last_name']


class UserLoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))


class UserCreateForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'role', 'phone', 'profile_picture', 'academic_level']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})


# Provide a VideoForm alias for compatibility with older imports
class VideoForm(VideoUploadForm):
    """Alias/wrapper around VideoUploadForm kept for compatibility."""
    pass


# Inline formset for Course -> Video (used by dashboard)
VideoFormSet = inlineformset_factory(
    Course,
    Video,
    fields=['title', 'description', 'url', 'course', 'level', 'subject', 'stream', 'teacher', 'cost', 'image'],
    extra=1,
    can_delete=True,
)


# Backwards-compatible name used earlier in the dashboard code
VideoFormSetInline = VideoFormSet