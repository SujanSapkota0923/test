
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):

    class Role(models.TextChoices):
        ADMIN = "admin", "Admin"
        TEACHER = "teacher", "Teacher"
        STUDENT = "student", "Student"
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.STUDENT)
    phone = models.CharField(max_length=20, blank=True, null=True)
    bio = models.TextField(blank=True) # this will be added after profile is created
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    academic_level = models.ForeignKey(
        'AcademicLevel',
        on_delete=models.SET_NULL,  # If the academic level is deleted, set student.academic_level to NULL
        blank=True,
        null=True,
        related_name='students'
    )
    def save(self, *args, **kwargs):
        if self.role == self.Role.ADMIN:
            self.is_staff = True
        super().save(*args, **kwargs)

    def clean(self):
        super().clean()
        # if self.role == self.Role.STUDENT and not self.academic_level:
        #     raise ValidationError("A student must have an academic level.")
        if self.role != self.Role.STUDENT and self.academic_level:
            raise ValidationError("Only students can have an academic level.")

    @property
    def is_teacher(self):
        return self.role == self.Role.TEACHER

    @property
    def is_student(self):
        return self.role == self.Role.STUDENT
    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN

    # if user is student then only return name with student
    def __str__(self):
        if self.is_student:
            return f"{self.username} (Student)"
        return f"{self.username}"

    def get_current_enrollment(self):
        """Get the student's current active enrollment"""
        try:
            return self.enrollments.get(is_active=True)
        except Enrollment.DoesNotExist:
            return None
        except Enrollment.MultipleObjectsReturned:
            # Should not happen with validation, but handle it
            return self.enrollments.filter(is_active=True).first()
        
class AcademicLevel(models.Model): # for representing grades/years 1 for class one and 2 for class two
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True) # for URL use like 'grade-10', 'bachelor', etc. for easy referencing
    order = models.IntegerField(help_text="Sorting order (smaller -> earlier in schooling).")
    # Optional: marks whether this level can have streams (like +2)
    allows_streams = models.BooleanField(default=False)
    capacity = models.PositiveIntegerField(blank=True, null=True, help_text="Maximum number of students allowed in this level (optional).")
    # all students from this academic level can be accessed by related_name 'students' from User model

    class Meta: 
        ordering = ("order",)
        verbose_name = "Academic Level"
        verbose_name_plural = "Academic Levels"
    
    def capacity_remaining(self):
        if self.capacity is None:
            return "Not set"  # Unlimited capacity
        enrolled_count = self.enrollments.filter(is_active=True).count()
        return self.capacity - enrolled_count

    def __str__(self):
        return self.name


class Stream(models.Model):
    """
    Optional division inside some AcademicLevels (e.g. +2 Science, +2 Management).
    Only attach Streams to AcademicLevels where allows_streams=True.
    """
    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=50)
    level = models.ForeignKey(AcademicLevel, related_name="streams", on_delete=models.CASCADE)

    class Meta:
        unique_together = ("name", 'level')

    def clean(self):
        if not self.level.allows_streams:
            raise ValidationError("Cannot add a Stream to an AcademicLevel that doesn't allow streams.")

    def __str__(self):
        return f"{self.level.name} — {self.name}"


class Subject(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    levels = models.ForeignKey(AcademicLevel, related_name="subjects", on_delete=models.CASCADE, blank=True, null=True)
    streams = models.ManyToManyField(Stream, related_name="subjects", default=None, blank=True)

    def unique_together(self):
        return ("name", "levels")
    
    def ordering(self):
        return ("-",)
    
    def __str__(self):
        return self.name


class Enrollment(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="enrollments", on_delete=models.CASCADE, limit_choices_to={"role": User.Role.STUDENT})
    level = models.ForeignKey(AcademicLevel, related_name="enrollments", on_delete=models.CASCADE)
    joined_at = models.DateTimeField(default=timezone.now)
    left_at = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField(default=False)  # if false, student unenrolled/left

    # class Meta:
    #     unique_together = ("student", "level")
    
    def __str__(self):
        return f"{self.student.username}"

    # stop enrolling if the capacity of the level is full and update is_active to false and update the level
    def clean(self):
        super().clean()
        
        # Check if student already has an active enrollment
        if self.is_active:
            existing_active = Enrollment.objects.filter(
                student=self.student,
                is_active=True
            ).exclude(pk=self.pk)
            
            if existing_active.exists():
                raise ValidationError(
                    f"{self.student.username} is already enrolled in {existing_active.first().level.name}. "
                    "Please deactivate the current enrollment first."
                )
        
        # Check capacity (exclude current enrollment if updating)
        if self.level.capacity is not None and self.is_active:
            active_enrollments = Enrollment.objects.filter(
                level=self.level, 
                is_active=True
            ).exclude(pk=self.pk).count()
            
            if active_enrollments >= self.level.capacity:
                raise ValidationError(
                    f"The level {self.level.name} has reached its capacity of {self.level.capacity} students."
                )

    def save(self, *args, **kwargs):
        # Run clean validation
        self.full_clean()
        
        # Update student's academic_level when enrollment is active
        if self.is_active:
            self.student.academic_level = self.level
            self.student.save(update_fields=['academic_level'])
        
        # If deactivating enrollment, set left_at timestamp
        if not self.is_active and self.left_at is None:
            self.left_at = timezone.now()
        
        super().save(*args, **kwargs)
    

class LiveClass(models.Model):
    """
    Represents a scheduled live class (online lecture).
    - host: teacher who created/hosts the class (optional multiple hosts via ManyToMany below)
    - subject: which subject the live class is about (optional)
    - section: the ClassSection (which determines the audience)
    - start_time / end_time: scheduling
    - meeting_url: link to Zoom / Jitsi / BigBlueButton (stored as text)
    - is_recorded: whether the session is recorded and where it can be found (optional)
    """
    title = models.CharField(max_length=200)
    level = models.ForeignKey(AcademicLevel, related_name="live_classes", on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, related_name="live_classes", on_delete=models.SET_NULL, null=True, blank=True)
    hosts = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="hosted_live_classes", limit_choices_to={"role": User.Role.TEACHER}, blank=True, null=True, help_text="Teachers hosting this live class")
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    meeting_url = models.URLField(max_length=500, blank=True, help_text="Link to join the live class (Zoom/Jitsi/...)", null=True)
    description = models.TextField(blank=True)
    is_recorded = models.BooleanField(default=False)
    recording_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    extra = models.JSONField(blank=True, null=True, help_text="Optional metadata (platform, meeting_id, dial-in info, etc.)")

    class Meta:
        ordering = ("-start_time",)

    def clean(self):
        # Check if both start_time and end_time are provided before comparing
        if self.start_time and self.end_time:
            if self.end_time <= self.start_time:
                raise ValidationError("end_time must be after start_time")
        # Ensure hosts are teachers (should be enforced by limit_choices_to but double-check)
        if self.hosts and self.hosts.role != User.Role.TEACHER:
            raise ValidationError("All hosts must be teachers.")

    def is_live(self):
        now = timezone.now()
        return self.start_time <= now <= self.end_time

    def will_start_soon(self, minutes=15):
        now = timezone.now()
        return 0 <= (self.start_time - now).total_seconds() <= minutes * 60
    # returns true if the class to be started within fifteen minutes
    # for notification purpose

    def __str__(self):
        return f"{self.title} — {self.subject} ({self.start_time:%Y-%m-%d %H:%M})"

# extra curricular activities refers to course in this project.
class ExtraCurricularActivity(models.Model):
    '''
    Represents an extra-curricular activity or event.
    like all the sports activities, arts, debate club, or 
    extra stuff tought in schools/colleges like 
    coding, politics, and other informational etc.
    '''
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="extracurricular_activities", blank=True)
    cost = models.DecimalField(max_digits=8, decimal_places=2, default=0, help_text="Cost to participate in the activity (0 for free)")
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='activity_images/', blank=True, null=True)

    class Meta:
        ordering = ("-start_time",)

    def clean(self):
        # Check if both start_time and end_time are provided before comparing
        if self.start_time and self.end_time:
            if self.end_time <= self.start_time:
                raise ValidationError("end_time must be after start_time")

    def __str__(self):
        return self.title
    
class Video(models.Model):
    '''
    Represents stored videos related to courses or activities.
    '''
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    url = models.URLField(max_length=500, help_text="Link to the video (YouTube/Vimeo/...)", unique=True)
    level = models.ForeignKey(AcademicLevel, related_name="videos", on_delete=models.CASCADE, blank=True, null=True)
    course = models.ForeignKey(ExtraCurricularActivity, related_name="videos", on_delete=models.SET_NULL, null=True, blank=True)
    subject = models.ForeignKey(Subject, related_name="videos", on_delete=models.SET_NULL, null=True, blank=True)
    stream = models.ManyToManyField(Stream, related_name="videos", blank=True)
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="uploaded_videos", limit_choices_to={"role": User.Role.TEACHER}, blank=True, null=True, help_text="Must be a teacher")
    cost = models.DecimalField(max_digits=8, decimal_places=2, default=0, help_text="Cost to access the video (0.00 for free)")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='video_thumbnails/', blank=True, null=True)
    course = models.ForeignKey(ExtraCurricularActivity, related_name='videos', on_delete=models.CASCADE, blank=True, null=True)


    # if the cost is negative, raise validation error
    def clean(self):
        if self.cost < 0:
            raise ValidationError("Cost cannot be negative.")
        # Ensure teacher is indeed a teacher
        if self.teacher and self.teacher.role != User.Role.TEACHER:
            raise ValidationError("The uploader must be a teacher.")
        
    # if the cost is 0, show it as free
    @property
    def cost_display(self):
        return "Free" if self.cost == 0 else f"${self.cost:.2f}"


    def __str__(self):
        return self.title