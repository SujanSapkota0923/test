#!/usr/bin/env python3
"""
Comprehensive data population script for teaching portal
Generates realistic data with ALL images and files
"""
import os
import django
import sys
import random
from decimal import Decimal
from datetime import datetime, timedelta

# Setup Django environment
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Course_Management_system.settings')
django.setup()

from apps.Course.models import (
    User, AcademicLevel, Stream, Subject, Course, 
    PaymentMethod, PaymentVerification, LiveClass, Video
)
from django.core.files.base import ContentFile
from django.utils import timezone
from PIL import Image, ImageDraw, ImageFont
import io
import json

# Color schemes for images
COLORS = [
    '#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8',
    '#F7DC6F', '#BB8FCE', '#85C1E2', '#F8B739', '#52B788',
    '#E63946', '#457B9D', '#1D3557', '#F1FAEE', '#A8DADC'
]

SUBJECTS_DATA = [
    'Mathematics', 'Physics', 'Chemistry', 'Biology', 'Computer Science',
    'English Literature', 'History', 'Geography', 'Economics', 'Business Studies',
    'Art & Design', 'Music', 'Physical Education', 'Foreign Languages', 'Psychology'
]

COURSE_TOPICS = [
    'Introduction to Advanced', 'Fundamentals of', 'Mastering', 'Deep Dive into',
    'Complete Guide to', 'Professional', 'Practical', 'Advanced Techniques in'
]

FIRST_NAMES = [
    'Emma', 'Liam', 'Olivia', 'Noah', 'Ava', 'Ethan', 'Sophia', 'Mason',
    'Isabella', 'William', 'Mia', 'James', 'Charlotte', 'Benjamin', 'Amelia',
    'Lucas', 'Harper', 'Henry', 'Evelyn', 'Alexander', 'Abigail', 'Michael',
    'Emily', 'Daniel', 'Elizabeth', 'Matthew', 'Sofia', 'Jackson', 'Avery',
    'Sebastian', 'Ella', 'Jack', 'Scarlett', 'Aiden', 'Grace', 'Owen', 'Chloe',
    'Samuel', 'Victoria', 'Joseph', 'Riley', 'John', 'Aria', 'David', 'Lily'
]

LAST_NAMES = [
    'Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis',
    'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Gonzalez', 'Wilson', 'Anderson',
    'Thomas', 'Taylor', 'Moore', 'Jackson', 'Martin', 'Lee', 'Walker', 'Hall',
    'Allen', 'Young', 'King', 'Wright', 'Scott', 'Torres', 'Nguyen', 'Hill'
]

def create_profile_image(name, color):
    """Create a profile picture with initials"""
    size = (200, 200)
    img = Image.new('RGB', size, color=color)
    draw = ImageDraw.Draw(img)
    
    # Get initials
    parts = name.split()
    initials = ''.join([p[0].upper() for p in parts[:2]])
    
    # Draw circle background
    circle_color = tuple(int(color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
    lighter_color = tuple(min(c + 40, 255) for c in circle_color)
    draw.ellipse([20, 20, 180, 180], fill=lighter_color)
    
    # Draw initials
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 70)
    except:
        font = ImageFont.load_default()
    
    # Center text
    bbox = draw.textbbox((0, 0), initials, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (size[0] - text_width) / 2
    y = (size[1] - text_height) / 2 - 10
    
    draw.text((x, y), initials, fill='white', font=font)
    
    # Save to BytesIO
    img_io = io.BytesIO()
    img.save(img_io, format='PNG')
    img_io.seek(0)
    
    return ContentFile(img_io.read(), name=f'{name.replace(" ", "_")}_profile.png')

def create_payment_method_image(name, color):
    """Create payment method logo"""
    size = (300, 200)
    img = Image.new('RGB', size, color='white')
    draw = ImageDraw.Draw(img)
    
    # Background gradient effect
    bg_color = tuple(int(color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
    for i in range(size[1]):
        factor = i / size[1]
        shade = tuple(int(c * (0.7 + factor * 0.3)) for c in bg_color)
        draw.rectangle([0, i, size[0], i+1], fill=shade)
    
    # Draw payment method name
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 40)
    except:
        font = ImageFont.load_default()
    
    bbox = draw.textbbox((0, 0), name, font=font)
    text_width = bbox[2] - bbox[0]
    x = (size[0] - text_width) / 2
    y = size[1] / 2 - 20
    
    draw.text((x, y), name, fill='white', font=font)
    
    img_io = io.BytesIO()
    img.save(img_io, format='PNG')
    img_io.seek(0)
    
    return ContentFile(img_io.read(), name=f'{name.replace(" ", "_")}_logo.png')

def create_course_image(title, color):
    """Create course thumbnail"""
    size = (800, 450)
    img = Image.new('RGB', size, color=color)
    draw = ImageDraw.Draw(img)
    
    # Add some design elements
    base_color = tuple(int(color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
    darker = tuple(max(c - 40, 0) for c in base_color)
    
    # Draw some geometric shapes
    draw.ellipse([600, -50, 900, 250], fill=darker)
    draw.ellipse([-100, 300, 200, 600], fill=darker)
    
    # Draw title
    try:
        font_large = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 50)
        font_small = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 30)
    except:
        font_large = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    # Wrap text
    words = title.split()
    lines = []
    current_line = []
    for word in words:
        current_line.append(word)
        test_line = ' '.join(current_line)
        bbox = draw.textbbox((0, 0), test_line, font=font_large)
        if bbox[2] - bbox[0] > size[0] - 100:
            current_line.pop()
            lines.append(' '.join(current_line))
            current_line = [word]
    if current_line:
        lines.append(' '.join(current_line))
    
    # Draw lines
    y = 150
    for line in lines[:3]:  # Max 3 lines
        bbox = draw.textbbox((0, 0), line, font=font_large)
        text_width = bbox[2] - bbox[0]
        x = (size[0] - text_width) / 2
        draw.text((x, y), line, fill='white', font=font_large)
        y += 60
    
    img_io = io.BytesIO()
    img.save(img_io, format='PNG')
    img_io.seek(0)
    
    return ContentFile(img_io.read(), name=f'{title[:30].replace(" ", "_")}_course.png')

def create_payment_proof(amount):
    """Create payment proof/receipt image"""
    size = (600, 800)
    img = Image.new('RGB', size, color='white')
    draw = ImageDraw.Draw(img)
    
    # Header
    draw.rectangle([0, 0, size[0], 100], fill='#2C3E50')
    
    try:
        font_title = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 40)
        font_text = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 25)
    except:
        font_title = ImageFont.load_default()
        font_text = ImageFont.load_default()
    
    # Title
    draw.text((150, 30), "PAYMENT RECEIPT", fill='white', font=font_title)
    
    # Details
    y = 150
    details = [
        f"Amount: ${amount}",
        f"Date: {datetime.now().strftime('%Y-%m-%d')}",
        f"Transaction ID: TXN{random.randint(10000, 99999)}",
        "Status: COMPLETED",
        "",
        "Thank you for your payment!"
    ]
    
    for detail in details:
        draw.text((50, y), detail, fill='#2C3E50', font=font_text)
        y += 50
    
    # Footer
    draw.rectangle([0, size[1]-80, size[0], size[1]], fill='#ECF0F1')
    draw.text((180, size[1]-55), "Official Receipt", fill='#7F8C8D', font=font_text)
    
    img_io = io.BytesIO()
    img.save(img_io, format='PNG')
    img_io.seek(0)
    
    return ContentFile(img_io.read(), name=f'receipt_{random.randint(1000, 9999)}.png')

def populate_database():
    print("=" * 80)
    print("🚀 COMPREHENSIVE DATA POPULATION - TEACHING PORTAL")
    print("=" * 80)
    print("\n📋 This will create:")
    print("   - Admin users with profiles")
    print("   - 50 Students with profile pictures")
    print("   - 20 Teachers with profile pictures")
    print("   - Academic levels and streams")
    print("   - 15 Subjects")
    print("   - 25 Courses with images")
    print("   - 5 Payment methods with logos")
    print("   - 30 Payment verifications with receipts")
    print("   - 20 Live classes")
    print("   - 30 Video lectures")
    print("\n" + "=" * 80)
    
    # 1. CREATE ADMIN USERS
    print("\n👤 Creating Admin Users...")
    admins_data = [
        ('admin', 'admin@portal.com', 'Admin', 'User', 'admin123'),
        ('a', 'a@admin.com', 'Super', 'Admin', 'a'),
    ]
    
    admins = []
    for username, email, first, last, password in admins_data:
        admin, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': email,
                'first_name': first,
                'last_name': last,
                'role': User.Role.ADMIN,
                'is_staff': True,
                'is_superuser': True,
                'phone': f'+1-555-{random.randint(100, 999)}-{random.randint(1000, 9999)}',
                'bio': f'{first} {last} - System Administrator with full access to manage the teaching portal.'
            }
        )
        if created:
            admin.set_password(password)
            admin.profile_picture = create_profile_image(f'{first} {last}', random.choice(COLORS))
            admin.save()
            print(f"   ✓ Created admin: {username} (password: {password})")
        else:
            print(f"   ⚠️  Admin exists: {username}")
        admins.append(admin)
    
    # 2. CREATE ACADEMIC LEVELS
    print("\n📚 Creating Academic Levels...")
    levels_data = [
        ('Level 1', 'level-1', 1, True, 100),
        ('Level 2', 'level-2', 2, True, 100),
        ('Level 3', 'level-3', 3, True, 100),
        ('Level 4', 'level-4', 4, True, 100),
        ('Level 5', 'level-5', 5, True, 100),
    ]
    
    levels = []
    for name, slug, order, allows_streams, capacity in levels_data:
        level, created = AcademicLevel.objects.get_or_create(
            name=name,
            defaults={'slug': slug, 'order': order, 'allows_streams': allows_streams, 'capacity': capacity}
        )
        levels.append(level)
        status = "✓ Created" if created else "⚠️  Exists"
        print(f"   {status}: {name}")
    
    # 3. CREATE STREAMS
    print("\n🎯 Creating Streams...")
    streams_data = [
        ('Science', 'science'),
        ('Commerce', 'commerce'),
        ('Arts', 'arts'),
        ('Technology', 'technology'),
        ('Medical', 'medical'),
    ]
    
    streams = []
    for name, slug in streams_data:
        # Attach to levels that allow streams (Level 4 and 5)
        for level in [l for l in levels if l.allows_streams]:
            stream, created = Stream.objects.get_or_create(
                name=name,
                level=level,
                defaults={'slug': slug}
            )
            if level == levels[-1]:  # Only add to list once
                streams.append(stream)
            if created:
                status = "✓ Created"
                print(f"   {status}: {name} in {level.name}")
                break
    
    # 4. CREATE TEACHERS
    print("\n👨‍🏫 Creating 20 Teachers with profile pictures...")
    teachers = []
    for i in range(20):
        first_name = random.choice(FIRST_NAMES)
        last_name = random.choice(LAST_NAMES)
        username = f'teacher_{first_name.lower()}{i+1}'
        
        teacher, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': f'{username}@school.edu',
                'first_name': first_name,
                'last_name': last_name,
                'role': User.Role.TEACHER,
                'phone': f'+1-555-{random.randint(100, 999)}-{random.randint(1000, 9999)}',
                'bio': f'Experienced educator specializing in {random.choice(SUBJECTS_DATA)}. Passionate about student success and innovative teaching methods.',
                'academic_level': random.choice(levels)
            }
        )
        
        if created:
            teacher.set_password('teacher123')
            teacher.profile_picture = create_profile_image(f'{first_name} {last_name}', random.choice(COLORS))
            teacher.save()
            print(f"   ✓ Created: {teacher.get_full_name()} (@{username})")
        teachers.append(teacher)
    
    # 5. CREATE STUDENTS
    print("\n👨‍🎓 Creating 50 Students with profile pictures...")
    students = []
    for i in range(50):
        first_name = random.choice(FIRST_NAMES)
        last_name = random.choice(LAST_NAMES)
        username = f'student_{first_name.lower()}{last_name.lower()}{i+1}'
        
        student, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': f'{username}@students.edu',
                'first_name': first_name,
                'last_name': last_name,
                'role': User.Role.STUDENT,
                'phone': f'+1-555-{random.randint(100, 999)}-{random.randint(1000, 9999)}',
                'bio': f'Dedicated student pursuing excellence in academics. Interested in {random.choice(SUBJECTS_DATA)} and extracurricular activities.',
                'academic_level': random.choice(levels)
            }
        )
        
        if created:
            student.set_password('student123')
            student.profile_picture = create_profile_image(f'{first_name} {last_name}', random.choice(COLORS))
            student.save()
            if i % 10 == 0:
                print(f"   ✓ Created {i+1}/50 students...")
        students.append(student)
    print(f"   ✓ All 50 students created!")
    
    # 6. CREATE SUBJECTS
    print("\n📖 Creating 15 Subjects...")
    subjects = []
    for i, subject_name in enumerate(SUBJECTS_DATA):
        assigned_level = random.choice(levels)
        assigned_streams = random.sample(streams, k=min(len(streams), random.randint(1, 3))) if streams else []
        
        subject, created = Subject.objects.get_or_create(
            name=subject_name,
            levels=assigned_level,
            defaults={
                'description': f'Comprehensive {subject_name} curriculum covering fundamental to advanced concepts.',
            }
        )
        
        if created:
            subject.streams.set(assigned_streams)
            print(f"   ✓ Created: {subject_name}")
        subjects.append(subject)
    
    # 7. CREATE COURSES
    print("\n🎓 Creating 25 Courses with images...")
    courses = []
    for i in range(25):
        topic = random.choice(COURSE_TOPICS)
        subject = random.choice(SUBJECTS_DATA)
        title = f'{topic} {subject}'
        
        start_time = timezone.now() + timedelta(days=random.randint(1, 30))
        end_time = start_time + timedelta(days=random.randint(30, 90))
        
        course, created = Course.objects.get_or_create(
            title=title,
            defaults={
                'description': f'This comprehensive course covers all aspects of {subject}. Students will learn through interactive lectures, practical exercises, and real-world applications. Perfect for those looking to master {subject} concepts.',
                'cost': Decimal(str(random.randint(500, 5000))),
                'start_time': start_time,
                'end_time': end_time
            }
        )
        
        if created:
            course.image = create_course_image(title, random.choice(COLORS))
            # Add random participants
            participants = random.sample(students, k=random.randint(5, 15))
            course.participants.set(participants)
            course.save()
            print(f"   ✓ Created: {title} (${course.cost})")
        courses.append(course)
    
    # 8. CREATE PAYMENT METHODS
    print("\n💳 Creating 5 Payment Methods with logos...")
    payment_methods_data = [
        ('Bank Transfer', 'Direct bank transfer to school account', {
            'bank_name': 'National Bank',
            'account_number': '1234567890',
            'account_name': 'School Education Fund',
            'routing_number': '123456789',
            'swift_code': 'NATBANKXXX'
        }),
        ('Credit/Debit Card', 'Pay securely with your credit or debit card', {
            'accepted_cards': ['Visa', 'Mastercard', 'American Express'],
            'processor': 'Stripe Payment Gateway'
        }),
        ('Mobile Money', 'Pay via mobile money transfer', {
            'providers': ['M-Pesa', 'Airtel Money', 'MTN Mobile Money'],
            'number': '+1-555-PAY-SCHOOL'
        }),
        ('Cash Payment', 'Pay in cash at school office', {
            'office_hours': 'Mon-Fri: 9AM-5PM',
            'location': 'Administration Building, Room 101'
        }),
        ('Online Banking', 'Pay through your online banking portal', {
            'payment_reference': 'SCHOOL-FEES',
            'institution_code': 'EDU-123'
        }),
    ]
    
    payment_methods = []
    for i, (name, desc, details) in enumerate(payment_methods_data):
        pm, created = PaymentMethod.objects.get_or_create(
            name=name,
            defaults={
                'description': desc,
                'details': json.dumps(details),
                'is_active': True,
                'display_order': i + 1,
                'created_by': random.choice(admins)
            }
        )
        
        if created:
            pm.image = create_payment_method_image(name, random.choice(COLORS))
            pm.save()
            print(f"   ✓ Created: {name}")
        payment_methods.append(pm)
    
    # 9. CREATE PAYMENT VERIFICATIONS
    print("\n💰 Creating 30 Payment Verifications with receipts...")
    transaction_base = 100000
    for i in range(30):
        student = random.choice(students)
        course = random.choice(courses)
        payment_method = random.choice(payment_methods)
        amount = course.cost
        
        # Check if already exists
        existing = PaymentVerification.objects.filter(
            user=student,
            course=course,
            payment_method=payment_method
        ).first()
        
        if existing:
            continue
        
        verified = random.random() > 0.5  # 50% chance of being verified
        
        payment = PaymentVerification.objects.create(
            user=student,
            course=course,
            payment_method=payment_method,
            amount=amount,
            transaction_id=f'TXN{transaction_base + i}',
            remarks=random.choice([
                'Payment made via online transfer. Please verify.',
                'Paid in full for course enrollment.',
                'First installment payment completed.',
                'Urgent payment for immediate enrollment.',
                'Early bird discount applied.',
            ]),
            verified=verified
        )
        
        # Add payment proof
        payment.payment_proof = create_payment_proof(amount)
        
        if verified:
            payment.verified_by = random.choice(admins)
            payment.verification_notes = random.choice([
                'Payment verified and approved. Student enrolled successfully.',
                'Transaction confirmed. Welcome to the course!',
                'Payment received and verified. Enrollment complete.',
                'Verified. Payment matches bank records.',
            ])
            payment.verified_at = timezone.now() - timedelta(days=random.randint(1, 10))
            # Enroll student in course
            student.course = course
            student.save()
        
        payment.save()
        
        if i % 5 == 0:
            print(f"   ✓ Created {i+1}/30 payment verifications...")
    
    print(f"   ✓ All payment verifications created!")
    
    # 10. CREATE LIVE CLASSES
    print("\n📹 Creating 20 Live Classes...")
    for i in range(20):
        subject = random.choice(subjects)
        teacher = random.choice(teachers)
        level = random.choice(levels)
        course = random.choice(courses)
        
        start_time = timezone.now() + timedelta(days=random.randint(1, 14), hours=random.randint(8, 17))
        end_time = start_time + timedelta(hours=random.choice([1, 1.5, 2]))
        
        live_class, created = LiveClass.objects.get_or_create(
            title=f'{subject.name} - Live Session {i+1}',
            defaults={
                'description': f'Interactive live class on {subject.name}. Join us for an engaging session with Q&A.',
                'subject': subject,
                'hosts': teacher,
                'level': level,
                'course': course,
                'start_time': start_time,
                'end_time': end_time,
                'meeting_url': f'https://meet.school.edu/class-{random.randint(10000, 99999)}',
                'is_recorded': random.random() > 0.5,
                'recording_url': f'https://recordings.school.edu/{random.randint(10000, 99999)}' if random.random() > 0.5 else None
            }
        )
        
        if created and i % 5 == 0:
            print(f"   ✓ Created {i+1}/20 live classes...")
    
    print(f"   ✓ All live classes created!")
    
    # 11. CREATE VIDEO LECTURES
    print("\n🎬 Creating 30 Video Lectures...")
    for i in range(30):
        subject = random.choice(subjects)
        teacher = random.choice(teachers)
        level = random.choice(levels)
        course = random.choice(courses)
        
        video, created = Video.objects.get_or_create(
            url=f'https://video.school.edu/watch/{random.randint(10000, 99999)}',
            defaults={
                'title': f'{subject.name} - Lecture {i+1}',
                'description': f'Recorded lecture covering important topics in {subject.name}. Includes examples and practice problems.',
                'subject': subject,
                'teacher': teacher,
                'level': level,
                'course': course,
                'cost': Decimal(str(random.choice([0, 50, 100, 150, 200])))
            }
        )
        
        if created:
            # Add streams (ManyToMany)
            video.stream.set(random.sample(streams, k=min(len(streams), random.randint(1, 2))))
            # Create thumbnail
            video.image = create_course_image(f'{subject.name} Video', random.choice(COLORS))
            video.save()
            
            if i % 10 == 0:
                print(f"   ✓ Created {i+1}/30 video lectures...")
    
    print(f"   ✓ All video lectures created!")
    
    # FINAL STATISTICS
    print("\n" + "=" * 80)
    print("📊 FINAL STATISTICS")
    print("=" * 80)
    print(f"   👤 Total Users: {User.objects.count()}")
    print(f"      - Admins: {User.objects.filter(role='admin').count()}")
    print(f"      - Teachers: {User.objects.filter(role='teacher').count()}")
    print(f"      - Students: {User.objects.filter(role='student').count()}")
    print(f"   📚 Academic Levels: {AcademicLevel.objects.count()}")
    print(f"   🎯 Streams: {Stream.objects.count()}")
    print(f"   📖 Subjects: {Subject.objects.count()}")
    print(f"   🎓 Courses: {Course.objects.count()}")
    print(f"   💳 Payment Methods: {PaymentMethod.objects.count()}")
    print(f"   💰 Payment Verifications: {PaymentVerification.objects.count()}")
    print(f"      - Pending: {PaymentVerification.objects.filter(verified=False).count()}")
    print(f"      - Verified: {PaymentVerification.objects.filter(verified=True).count()}")
    print(f"   📹 Live Classes: {LiveClass.objects.count()}")
    print(f"   🎬 Video Lectures: {Video.objects.count()}")
    print("=" * 80)
    print("\n✅ DATABASE FULLY POPULATED WITH ALL IMAGES AND FILES!")
    print("\n🌐 Login Credentials:")
    print("   Admin: username=a, password=a")
    print("   Teachers: username=teacher_*, password=teacher123")
    print("   Students: username=student_*, password=student123")
    print("\n🚀 Start server: python3 manage.py runserver 0.0.0.0:8000")
    print("=" * 80)

if __name__ == '__main__':
    try:
        populate_database()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

