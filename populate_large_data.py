#!/usr/bin/env python3
"""
Comprehensive Large-Scale Data Population Script
Generates authentic data for the Course Management System
"""

import os
import sys
import django
from pathlib import Path
import random
from datetime import datetime, timedelta
from decimal import Decimal
import json

# Setup Django
sys.path.append(str(Path(__file__).parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Course_Management_system.settings')
django.setup()

from django.utils import timezone
from django.contrib.auth.hashers import make_password
from apps.Course.models import (
    User, AcademicLevel, Stream, Subject, Course, 
    LiveClass, Video, PaymentMethod, PaymentVerification
)
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from django.core.files.base import ContentFile

# ============================================
# AUTHENTIC DATA POOLS
# ============================================

FIRST_NAMES = [
    # Male names
    "Liam", "Noah", "Oliver", "Elijah", "James", "William", "Benjamin", "Lucas", "Henry", "Alexander",
    "Mason", "Michael", "Ethan", "Daniel", "Jacob", "Logan", "Jackson", "Levi", "Sebastian", "Mateo",
    "Jack", "Owen", "Theodore", "Aiden", "Samuel", "Joseph", "John", "David", "Wyatt", "Matthew",
    "Luke", "Asher", "Carter", "Julian", "Grayson", "Leo", "Jayden", "Gabriel", "Isaac", "Lincoln",
    "Anthony", "Hudson", "Dylan", "Ezra", "Thomas", "Charles", "Christopher", "Jaxon", "Maverick", "Josiah",
    # Female names
    "Emma", "Olivia", "Ava", "Isabella", "Sophia", "Charlotte", "Mia", "Amelia", "Harper", "Evelyn",
    "Abigail", "Emily", "Elizabeth", "Mila", "Ella", "Avery", "Sofia", "Camila", "Aria", "Scarlett",
    "Victoria", "Madison", "Luna", "Grace", "Chloe", "Penelope", "Layla", "Riley", "Zoey", "Nora",
    "Lily", "Eleanor", "Hannah", "Lillian", "Addison", "Aubrey", "Ellie", "Stella", "Natalie", "Zoe",
    "Leah", "Hazel", "Violet", "Aurora", "Savannah", "Audrey", "Brooklyn", "Bella", "Claire", "Skylar"
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez",
    "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin",
    "Lee", "Perez", "Thompson", "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson",
    "Walker", "Young", "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores",
    "Green", "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell", "Carter", "Roberts",
    "Phillips", "Evans", "Turner", "Parker", "Collins", "Edwards", "Stewart", "Morris", "Rogers", "Reed"
]

SUBJECT_AREAS = {
    "Mathematics": ["Algebra", "Geometry", "Calculus", "Statistics", "Trigonometry", "Number Theory", "Linear Algebra", "Discrete Mathematics"],
    "Science": ["Physics", "Chemistry", "Biology", "Environmental Science", "Astronomy", "Geology", "Oceanography"],
    "Computer Science": ["Programming Fundamentals", "Data Structures", "Algorithms", "Web Development", "Mobile App Development", "Database Systems", "Artificial Intelligence", "Machine Learning", "Cybersecurity"],
    "Languages": ["English Literature", "Creative Writing", "Spanish", "French", "Mandarin Chinese", "German", "Japanese", "Latin"],
    "Social Studies": ["World History", "American History", "Geography", "Economics", "Political Science", "Sociology", "Anthropology", "Psychology"],
    "Arts": ["Visual Arts", "Music Theory", "Theater Arts", "Digital Art", "Photography", "Film Studies", "Dance", "Graphic Design"],
    "Physical Education": ["Fitness Training", "Team Sports", "Individual Sports", "Health Education", "Nutrition", "Yoga", "Swimming"],
    "Business": ["Business Administration", "Accounting", "Marketing", "Finance", "Entrepreneurship", "Management", "Business Ethics"]
}

COURSE_TITLES = [
    "Introduction to {subject}", "Advanced {subject}", "Fundamentals of {subject}",
    "Mastering {subject}", "Complete Guide to {subject}", "Professional {subject}",
    "{subject} for Beginners", "Practical {subject}", "Deep Dive into {subject}",
    "Advanced Techniques in {subject}", "{subject} Masterclass", "Applied {subject}",
    "Modern {subject}", "Essential {subject} Skills", "{subject} Workshop"
]

VIDEO_LESSON_TITLES = [
    "Lecture {num}: {topic}", "Understanding {topic}", "{topic} Explained",
    "Introduction to {topic}", "Advanced {topic} Concepts", "{topic} Tutorial",
    "Mastering {topic}", "{topic} - Part {num}", "Deep Dive: {topic}",
    "{topic} Fundamentals", "Practical {topic}", "{topic} Case Study"
]

BIO_TEMPLATES_STUDENT = [
    "Passionate student eager to learn and grow. Interested in {interest1} and {interest2}.",
    "Dedicated learner pursuing excellence in academics. Enjoys {interest1}, {interest2}, and {interest3}.",
    "Motivated student with strong interest in {interest1}. Also loves {interest2} and {interest3}.",
    "Enthusiastic learner committed to academic success. Passionate about {interest1} and {interest2}.",
    "Ambitious student striving for knowledge. Hobbies include {interest1}, {interest2}, and {interest3}."
]

BIO_TEMPLATES_TEACHER = [
    "Experienced educator with {years} years of teaching {subject}. Passionate about inspiring students.",
    "Dedicated teacher specializing in {subject}. Committed to student success and innovative teaching methods.",
    "{years}+ years of experience in education. Expert in {subject} and curriculum development.",
    "Professional educator focused on {subject}. Believes in making learning engaging and accessible.",
    "Passionate about teaching {subject}. {years} years of experience helping students achieve their goals."
]

STUDENT_INTERESTS = [
    "reading", "sports", "music", "coding", "art", "science", "mathematics", "writing",
    "photography", "gaming", "robotics", "debate", "theater", "dancing", "cooking",
    "traveling", "volunteering", "chess", "astronomy", "history"
]

MEETING_PLATFORMS = [
    "https://zoom.us/j/{}",
    "https://meet.google.com/{}",
    "https://teams.microsoft.com/l/meetup-join/{}",
    "https://jitsi.org/{}"
]

VIDEO_PLATFORMS = [
    "https://www.youtube.com/watch?v={}",
    "https://vimeo.com/{}",
    "https://www.dailymotion.com/video/{}"
]

PAYMENT_METHODS_DATA = [
    {"name": "PayPal", "desc": "Pay securely with your PayPal account"},
    {"name": "Credit Card", "desc": "Visa, Mastercard, American Express"},
    {"name": "Bank Transfer", "desc": "Direct bank account transfer"},
    {"name": "Stripe", "desc": "Secure online payment processing"},
    {"name": "Venmo", "desc": "Mobile payment service"},
    {"name": "Cash App", "desc": "Peer-to-peer payment"},
    {"name": "Apple Pay", "desc": "Pay with your Apple device"},
    {"name": "Google Pay", "desc": "Fast, simple checkout"}
]

# ============================================
# UTILITY FUNCTIONS
# ============================================

def generate_username(first_name, last_name, existing_usernames):
    """Generate unique username"""
    base = f"{first_name.lower()}{last_name.lower()}"
    username = base
    counter = 1
    while username in existing_usernames:
        username = f"{base}{counter}"
        counter += 1
    existing_usernames.add(username)
    return username

def generate_email(username):
    """Generate email address"""
    domains = ["gmail.com", "yahoo.com", "outlook.com", "edu.com", "student.edu", "mail.com"]
    return f"{username}@{random.choice(domains)}"

def generate_phone():
    """Generate phone number"""
    return f"+1-{random.randint(200, 999)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}"

def generate_profile_image(first_name, last_name):
    """Generate a simple profile image with initials"""
    # Create image
    size = (200, 200)
    colors = [
        '#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8',
        '#F7DC6F', '#BB8FCE', '#85C1E2', '#F8B739', '#52B788'
    ]
    
    img = Image.new('RGB', size, random.choice(colors))
    draw = ImageDraw.Draw(img)
    
    # Draw initials
    initials = f"{first_name[0]}{last_name[0]}".upper()
    
    # Use default font
    font_size = 80
    # Calculate text position (center)
    bbox = draw.textbbox((0, 0), initials, font=None)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    position = ((size[0] - text_width) // 2, (size[1] - text_height) // 2 - 10)
    
    draw.text(position, initials, fill='white', font=None)
    
    # Save to BytesIO
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    
    filename = f"{first_name}_{last_name}_profile.png"
    return ContentFile(buffer.read(), name=filename)

def generate_course_image(title):
    """Generate a course/activity image"""
    size = (800, 400)
    colors = [
        '#2C3E50', '#E74C3C', '#3498DB', '#2ECC71', '#F39C12',
        '#9B59B6', '#1ABC9C', '#34495E', '#16A085', '#27AE60'
    ]
    
    img = Image.new('RGB', size, random.choice(colors))
    draw = ImageDraw.Draw(img)
    
    # Draw title (first 30 chars)
    short_title = title[:30] + "..." if len(title) > 30 else title
    
    # Simple centered text
    bbox = draw.textbbox((0, 0), short_title, font=None)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    position = ((size[0] - text_width) // 2, (size[1] - text_height) // 2)
    
    draw.text(position, short_title, fill='white', font=None)
    
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    
    filename = f"{'_'.join(title.split()[:3])}_course.png"
    return ContentFile(buffer.read(), name=filename)

def random_date_range(days_back=365, duration_days=(1, 90)):
    """Generate random start and end dates"""
    start = timezone.now() - timedelta(days=random.randint(0, days_back))
    duration = random.randint(duration_days[0], duration_days[1])
    end = start + timedelta(days=duration)
    return start, end

def random_class_time(days_ahead=30):
    """Generate random class time in the future or past"""
    if days_ahead < 0:
        # For past dates
        start = timezone.now() + timedelta(
            days=random.randint(days_ahead, 0),
            hours=random.randint(8, 18),
            minutes=random.choice([0, 15, 30, 45])
        )
    else:
        # For future dates
        start = timezone.now() + timedelta(
            days=random.randint(0, days_ahead),
            hours=random.randint(8, 18),
            minutes=random.choice([0, 15, 30, 45])
        )
    duration = random.choice([30, 45, 60, 90, 120])
    end = start + timedelta(minutes=duration)
    return start, end

# ============================================
# MAIN POPULATION FUNCTION
# ============================================

def populate_all():
    """Main function to populate all data"""
    
    print("\n" + "="*60)
    print("  COMPREHENSIVE DATA POPULATION SCRIPT")
    print("="*60 + "\n")
    
    # Clear existing data (optional - comment out if you want to keep existing data)
    print("🗑️  Clearing existing data...")
    PaymentVerification.objects.all().delete()
    Video.objects.all().delete()
    LiveClass.objects.all().delete()
    Course.objects.all().delete()
    PaymentMethod.objects.all().delete()
    Subject.objects.all().delete()
    Stream.objects.all().delete()
    User.objects.filter(is_superuser=False).delete()
    AcademicLevel.objects.all().delete()
    print("✓ Existing data cleared\n")
    
    # Track created objects
    existing_usernames = set()
    
    # ============================================
    # 1. CREATE ACADEMIC LEVELS
    # ============================================
    print("📚 Creating Academic Levels...")
    levels_data = [
        ("Kindergarten", "kindergarten", 1, False, 50),
        ("Grade 1", "grade-1", 2, False, 60),
        ("Grade 2", "grade-2", 3, False, 60),
        ("Grade 3", "grade-3", 4, False, 60),
        ("Grade 4", "grade-4", 5, False, 65),
        ("Grade 5", "grade-5", 6, False, 65),
        ("Grade 6", "grade-6", 7, False, 70),
        ("Grade 7", "grade-7", 8, False, 70),
        ("Grade 8", "grade-8", 9, False, 75),
        ("Grade 9", "grade-9", 10, False, 80),
        ("Grade 10", "grade-10", 11, False, 85),
        ("Grade 11", "grade-11", 12, True, 90),
        ("Grade 12", "grade-12", 13, True, 90),
        ("Undergraduate", "undergraduate", 14, True, 200),
        ("Graduate", "graduate", 15, True, 100),
    ]
    
    levels = {}
    for name, slug, order, allows_streams, capacity in levels_data:
        level = AcademicLevel.objects.create(
            name=name,
            slug=slug,
            order=order,
            allows_streams=allows_streams,
            capacity=capacity
        )
        levels[name] = level
    print(f"✓ Created {len(levels)} academic levels\n")
    
    # ============================================
    # 2. CREATE STREAMS
    # ============================================
    print("🌊 Creating Streams...")
    streams_data = {
        "Grade 11": ["Science", "Management", "Humanities"],
        "Grade 12": ["Science", "Management", "Humanities"],
        "Undergraduate": ["Computer Science", "Business Administration", "Engineering", "Arts & Humanities", "Natural Sciences"],
        "Graduate": ["MBA", "MS Computer Science", "MS Engineering", "MA Education"]
    }
    
    streams = {}
    stream_count = 0
    for level_name, stream_names in streams_data.items():
        level = levels[level_name]
        streams[level_name] = []
        for stream_name in stream_names:
            stream = Stream.objects.create(
                name=stream_name,
                slug=stream_name.lower().replace(' ', '-'),
                level=level
            )
            streams[level_name].append(stream)
            stream_count += 1
    print(f"✓ Created {stream_count} streams\n")
    
    # ============================================
    # 3. CREATE SUBJECTS
    # ============================================
    print("📖 Creating Subjects...")
    subjects = []
    subject_count = 0
    
    for category, subject_list in SUBJECT_AREAS.items():
        for subject_name in subject_list:
            # Assign to relevant levels
            relevant_levels = []
            if "Calculus" in subject_name or "Linear Algebra" in subject_name:
                relevant_levels = [levels["Grade 11"], levels["Grade 12"], levels["Undergraduate"]]
            elif category in ["Computer Science", "Business"]:
                relevant_levels = [levels["Grade 10"], levels["Grade 11"], levels["Grade 12"], levels["Undergraduate"]]
            else:
                # General subjects
                level_names = random.sample(list(levels.keys()), k=random.randint(3, 7))
                relevant_levels = [levels[ln] for ln in level_names]
            
            for level in relevant_levels:
                description = f"Comprehensive study of {subject_name.lower()} covering fundamental concepts and advanced topics."
                subject = Subject.objects.create(
                    name=subject_name,
                    description=description,
                    levels=level
                )
                
                # Add streams if level allows
                if level.allows_streams and level.name in streams:
                    # Add relevant streams
                    relevant_streams = []
                    if category == "Computer Science":
                        relevant_streams = [s for s in streams[level.name] if "Computer Science" in s.name or "Science" in s.name or "Engineering" in s.name]
                    elif category == "Business":
                        relevant_streams = [s for s in streams[level.name] if "Business" in s.name or "Management" in s.name or "MBA" in s.name]
                    elif category == "Science":
                        relevant_streams = [s for s in streams[level.name] if "Science" in s.name or "Engineering" in s.name]
                    else:
                        relevant_streams = random.sample(streams[level.name], k=random.randint(1, len(streams[level.name])))
                    
                    if relevant_streams:
                        subject.streams.add(*relevant_streams)
                
                subjects.append(subject)
                subject_count += 1
    
    print(f"✓ Created {subject_count} subjects\n")
    
    # ============================================
    # 4. CREATE ADMIN USER
    # ============================================
    print("👤 Creating Admin User...")
    admin, created = User.objects.get_or_create(
        username="admin",
        defaults={
            "email": "admin@school.edu",
            "first_name": "System",
            "last_name": "Administrator",
            "role": User.Role.ADMIN,
            "is_staff": True,
            "is_superuser": True,
            "phone": generate_phone(),
            "bio": "System administrator with full access to all features and settings.",
            "password": make_password("admin123")
        }
    )
    existing_usernames.add("admin")
    if created:
        print(f"✓ Created admin user (username: admin, password: admin123)\n")
    else:
        print(f"✓ Using existing admin user (username: admin)\n")
    
    # ============================================
    # 5. CREATE TEACHERS (50)
    # ============================================
    print("👨‍🏫 Creating Teachers...")
    teachers = []
    
    for i in range(50):
        first_name = random.choice(FIRST_NAMES)
        last_name = random.choice(LAST_NAMES)
        username = generate_username(first_name, last_name, existing_usernames)
        
        # Pick subject expertise
        expertise = random.choice(subjects)
        years = random.randint(3, 25)
        
        bio = random.choice(BIO_TEMPLATES_TEACHER).format(
            years=years,
            subject=expertise.name
        )
        
        teacher = User.objects.create(
            username=username,
            email=generate_email(username),
            first_name=first_name,
            last_name=last_name,
            role=User.Role.TEACHER,
            phone=generate_phone(),
            bio=bio,
            password=make_password("teacher123")
        )
        
        # Add profile picture (only for first 20 to save time)
        if i < 20:
            teacher.profile_picture = generate_profile_image(first_name, last_name)
            teacher.save()
        
        teachers.append(teacher)
        
        if (i + 1) % 20 == 0:
            print(f"  ✓ Created {i + 1} teachers...")
    
    print(f"✓ Created {len(teachers)} teachers\n")
    
    # ============================================
    # 6. CREATE STUDENTS (300)
    # ============================================
    print("👨‍🎓 Creating Students...")
    students = []
    
    for i in range(1000):
        first_name = random.choice(FIRST_NAMES)
        last_name = random.choice(LAST_NAMES)
        username = generate_username(first_name, last_name, existing_usernames)
        
        # Assign academic level
        level = random.choice(list(levels.values()))
        
        # Generate bio
        interests = random.sample(STUDENT_INTERESTS, 3)
        bio = random.choice(BIO_TEMPLATES_STUDENT).format(
            interest1=interests[0],
            interest2=interests[1],
            interest3=interests[2] if len(interests) > 2 else interests[0]
        )
        
        student = User.objects.create(
            username=username,
            email=generate_email(username),
            first_name=first_name,
            last_name=last_name,
            role=User.Role.STUDENT,
            academic_level=level,
            phone=generate_phone(),
            bio=bio,
            password=make_password("student123")
        )
        
        # Add profile picture (only for first 50 to save time)
        if i < 50:
            student.profile_picture = generate_profile_image(first_name, last_name)
            student.save()
        
        students.append(student)
        
        if (i + 1) % 100 == 0:
            print(f"  ✓ Created {i + 1} students...")
    
    print(f"✓ Created {len(students)} students\n")
    
    # ============================================
    # 7. CREATE COURSES (80)
    # ============================================
    print("🎓 Creating Courses...")
    courses = []
    
    for i in range(80):
        subject = random.choice(subjects)
        title = random.choice(COURSE_TITLES).format(subject=subject.name)
        
        description = f"""
        {title} is a comprehensive program designed to provide students with deep knowledge and practical skills.
        
        Course Highlights:
        • Expert instructors with years of experience
        • Hands-on projects and real-world applications
        • Interactive learning materials and resources
        • Flexible schedule with recorded sessions
        • Certificate of completion
        
        This course covers all essential topics in {subject.name} and prepares students for advanced concepts.
        Perfect for both beginners and those looking to enhance their skills.
        """.strip()
        
        start, end = random_date_range(days_back=180, duration_days=(30, 365))
        cost = Decimal(random.choice([0, 0, 0, 49.99, 99.99, 149.99, 199.99, 299.99, 499.99]))
        
        course = Course.objects.create(
            title=title,
            description=description,
            cost=cost,
            start_time=start,
            end_time=end
        )
        
        # Add image (only for first 30 to save time)
        if i < 30:
            course.image = generate_course_image(title)
            course.save()
        
        courses.append(course)
        
        if (i + 1) % 30 == 0:
            print(f"  ✓ Created {i + 1} courses...")
    
    print(f"✓ Created {len(courses)} courses\n")
    
    # ============================================
    # 8. ENROLL STUDENTS IN COURSES (60% enrollment rate)
    # ============================================
    print("📝 Enrolling Students in Courses...")
    enrollment_count = 0
    
    for student in students:
        # 60% chance of being enrolled
        if random.random() < 0.9:
            course = random.choice(courses)
            student.course = course
            student.save()
            enrollment_count += 1
    
    print(f"✓ Enrolled {enrollment_count} students in courses\n")
    
    # ============================================
    # 9. CREATE LIVE CLASSES (150)
    # ============================================
    print("📹 Creating Live Classes...")
    live_classes = []
    
    topics_by_subject = {}
    for subject in subjects:
        # Generate topic list for each subject
        topics = [
            f"Introduction to {subject.name}",
            f"Fundamentals of {subject.name}",
            f"Advanced {subject.name} Concepts",
            f"{subject.name} Applications",
            f"{subject.name} Case Studies",
            f"Practical {subject.name}",
            f"{subject.name} Workshop",
            f"Problem Solving in {subject.name}"
        ]
        topics_by_subject[subject.id] = topics
    
    for i in range(150):
        subject = random.choice(subjects)
        teacher = random.choice(teachers)
        level = subject.levels
        
        # Pick a course (30% chance)
        course = random.choice(courses) if random.random() < 0.3 else None
        
        # Generate topic
        topics = topics_by_subject[subject.id]
        topic = random.choice(topics)
        
        # Time: mix of past (30%), ongoing (10%), future (60%)
        rand = random.random()
        if rand < 0.3:  # Past
            start, end = random_class_time(days_ahead=-90)
        elif rand < 0.4:  # Ongoing
            start = timezone.now() - timedelta(minutes=random.randint(5, 30))
            end = start + timedelta(minutes=random.choice([45, 60, 90]))
        else:  # Future
            start, end = random_class_time(days_ahead=60)
        
        # Meeting URL
        meeting_id = ''.join(random.choices('0123456789abcdefghijklmnopqrstuvwxyz', k=10))
        meeting_url = random.choice(MEETING_PLATFORMS).format(meeting_id)
        
        # Description
        description = f"""
        Join us for an engaging session on {topic}.
        
        In this live class, we will cover:
        • Key concepts and principles
        • Practical examples and demonstrations
        • Q&A session with the instructor
        • Interactive exercises
        
        Prerequisites: Basic understanding of {subject.name}
        Duration: {(end - start).seconds // 60} minutes
        
        Don't miss this opportunity to learn from our expert instructor!
        """.strip()
        
        is_recorded = random.choice([True, False])
        recording_url = None
        if is_recorded and start < timezone.now():
            recording_url = random.choice(VIDEO_PLATFORMS).format(meeting_id + '-rec')
        
        live_class = LiveClass.objects.create(
            title=topic,
            course=course,
            level=level,
            subject=subject,
            hosts=teacher,
            start_time=start,
            end_time=end,
            meeting_url=meeting_url,
            description=description,
            is_recorded=is_recorded,
            recording_url=recording_url,
            extra=json.dumps({
                "platform": random.choice(["Zoom", "Google Meet", "Microsoft Teams", "Jitsi"]),
                "meeting_id": meeting_id,
                "password": ''.join(random.choices('0123456789', k=6)) if random.random() < 0.5 else None
            })
        )
        
        live_classes.append(live_class)
        
        if (i + 1) % 50 == 0:
            print(f"  ✓ Created {i + 1} live classes...")
    
    print(f"✓ Created {len(live_classes)} live classes\n")
    
    # ============================================
    # 10. CREATE VIDEOS (200)
    # ============================================
    print("🎬 Creating Videos...")
    videos = []
    
    for i in range(200):
        subject = random.choice(subjects)
        teacher = random.choice(teachers)
        level = subject.levels
        
        # Pick a course (40% chance)
        course = random.choice(courses) if random.random() < 0.4 else None
        
        # Generate lesson number and topic
        lesson_num = random.randint(1, 50)
        topics = topics_by_subject[subject.id]
        topic = random.choice(topics)
        
        title = random.choice(VIDEO_LESSON_TITLES).format(
            num=lesson_num,
            topic=topic
        )
        
        description = f"""
        Video lecture covering {topic} in detail.
        
        Topics covered:
        • {topic} fundamentals
        • Real-world applications
        • Step-by-step examples
        • Best practices and tips
        
        Instructor: {teacher.get_full_name()}
        Duration: {random.randint(15, 90)} minutes
        Level: {level.name}
        
        Watch this video to gain comprehensive understanding of the subject matter.
        """.strip()
        
        # Video URL
        video_id = ''.join(random.choices('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz_-', k=11))
        url = random.choice(VIDEO_PLATFORMS).format(video_id)
        
        cost = Decimal(random.choice([0, 0, 0, 0, 9.99, 19.99, 29.99, 49.99]))
        
        video = Video.objects.create(
            title=title,
            description=description,
            url=url,
            level=level,
            course=course,
            subject=subject,
            teacher=teacher,
            cost=cost
        )
        
        # Add streams if applicable
        if level.allows_streams and level.name in streams:
            video_streams = random.sample(streams[level.name], k=random.randint(1, len(streams[level.name])))
            video.stream.add(*video_streams)
        
        videos.append(video)
        
        if (i + 1) % 50 == 0:
            print(f"  ✓ Created {i + 1} videos...")
    
    print(f"✓ Created {len(videos)} videos\n")
    
    # ============================================
    # 11. CREATE PAYMENT METHODS (8)
    # ============================================
    print("💳 Creating Payment Methods...")
    payment_methods = []
    
    for idx, pm_data in enumerate(PAYMENT_METHODS_DATA):
        details = {
            "processing_fee": f"{random.uniform(0, 3):.2f}%",
            "processing_time": f"{random.randint(1, 5)} business days",
            "supported_currencies": random.sample(["USD", "EUR", "GBP", "CAD", "AUD"], k=3)
        }
        
        pm = PaymentMethod.objects.create(
            name=pm_data["name"],
            description=pm_data["desc"],
            details=json.dumps(details),
            is_active=random.choice([True, True, True, False]),  # 75% active
            display_order=idx,
            created_by=admin
        )
        
        payment_methods.append(pm)
    
    print(f"✓ Created {len(payment_methods)} payment methods\n")
    
    # ============================================
    # 12. CREATE PAYMENT VERIFICATIONS (100)
    # ============================================
    print("💰 Creating Payment Verifications...")
    verifications = []
    
    # Get active payment methods and paid courses
    active_pms = [pm for pm in payment_methods if pm.is_active]
    paid_courses = [c for c in courses if c.cost > 0]
    
    for i in range(100):
        student = random.choice(students)
        course = random.choice(paid_courses)
        pm = random.choice(active_pms)
        
        # Amount (usually course cost, sometimes slightly different)
        amount = course.cost
        if random.random() < 0.1:  # 10% pay different amount
            amount = amount + Decimal(random.uniform(-10, 10))
        
        transaction_id = f"TXN-{random.randint(100000, 999999)}-{random.randint(1000, 9999)}"
        
        remarks = random.choice([
            "Payment completed successfully",
            "Paid via online transfer",
            "Transaction confirmed",
            "Please verify payment",
            f"Reference: {transaction_id}",
            "Enrollment fee payment",
            ""
        ])
        
        # 70% verified, 30% pending
        is_verified = random.random() < 0.7
        verified_by = admin if is_verified else None
        verified_at = timezone.now() - timedelta(days=random.randint(1, 30)) if is_verified else None
        verification_notes = random.choice([
            "Payment verified successfully",
            "Amount matches course fee",
            "Transaction confirmed with payment provider",
            "Approved and processed",
            ""
        ]) if is_verified else ""
        
        created_at = timezone.now() - timedelta(days=random.randint(1, 60))
        
        pv = PaymentVerification.objects.create(
            user=student,
            course=course,
            payment_method=pm,
            amount=amount,
            transaction_id=transaction_id,
            remarks=remarks,
            verified=is_verified,
            verified_by=verified_by,
            verification_notes=verification_notes,
            verified_at=verified_at,
            created_at=created_at
        )
        
        verifications.append(pv)
        
        if (i + 1) % 50 == 0:
            print(f"  ✓ Created {i + 1} payment verifications...")
    
    print(f"✓ Created {len(verifications)} payment verifications\n")
    
    # ============================================
    # SUMMARY
    # ============================================
    print("\n" + "="*60)
    print("  ✅ DATA POPULATION COMPLETE!")
    print("="*60)
    print(f"""
    Summary:
    --------
    Academic Levels:       {AcademicLevel.objects.count()}
    Streams:               {Stream.objects.count()}
    Subjects:              {Subject.objects.count()}
    Users:
      - Admin:             1
      - Teachers:          {User.objects.filter(role=User.Role.TEACHER).count()}
      - Students:          {User.objects.filter(role=User.Role.STUDENT).count()}
    Courses:               {Course.objects.count()}
    Enrolled Students:     {User.objects.filter(course__isnull=False).count()}
    Live Classes:          {LiveClass.objects.count()}
    Videos:                {Video.objects.count()}
    Payment Methods:       {PaymentMethod.objects.count()}
    Payment Verifications: {PaymentVerification.objects.count()}
    
    Login Credentials:
    ------------------
    Admin:    username: admin     password: admin123
    Teacher:  username: (any teacher username)  password: teacher123
    Student:  username: (any student username)  password: student123
    
    """)
    print("="*60 + "\n")

# ============================================
# RUN SCRIPT
# ============================================

if __name__ == "__main__":
    try:
        populate_all()
    except KeyboardInterrupt:
        print("\n\n❌ Script interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error occurred: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
