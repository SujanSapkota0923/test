#!/usr/bin/env python3
"""
Script to create test payment verification data
Run with: python3 create_test_payments.py
"""
import os
import django
import sys
from decimal import Decimal

# Setup Django environment
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Course_Management_system.settings')
django.setup()

from apps.Course.models import User, Course, PaymentMethod, PaymentVerification
from django.core.files.base import ContentFile
from PIL import Image
import io

def create_test_payment_proof():
    """Create a simple test image for payment proof"""
    # Create a simple colored image
    img = Image.new('RGB', (400, 300), color='lightblue')
    
    # Save to BytesIO
    img_io = io.BytesIO()
    img.save(img_io, format='PNG')
    img_io.seek(0)
    
    return ContentFile(img_io.read(), name='test_payment_proof.png')

def create_test_data():
    print("Creating test payment verification data...\n")
    
    # Get students (users with role='student')
    students = User.objects.filter(role='student')[:5]
    if not students:
        print("❌ No students found! Please create some students first.")
        return
    
    print(f"✓ Found {students.count()} students")
    
    # Get courses
    courses = Course.objects.all()[:3]
    if not courses:
        print("❌ No courses found! Please create some courses first.")
        return
    
    print(f"✓ Found {courses.count()} courses")
    
    # Get payment methods
    payment_methods = PaymentMethod.objects.filter(is_active=True)
    if not payment_methods:
        print("❌ No active payment methods found! Please create payment methods first.")
        return
    
    print(f"✓ Found {payment_methods.count()} active payment methods\n")
    
    # Create test payment verifications - more data!
    test_data = [
        {
            'student': students[0],
            'course': courses[0],
            'amount': Decimal('5000.00'),
            'transaction_id': 'TXN001234567',
            'remarks': 'Payment made via online banking. Please verify.',
            'verified': False
        },
        {
            'student': students[1],
            'course': courses[1] if len(courses) > 1 else courses[0],
            'amount': Decimal('7500.50'),
            'transaction_id': 'TXN001234568',
            'remarks': 'Paid full amount for semester course.',
            'verified': False
        },
        {
            'student': students[2] if len(students) > 2 else students[0],
            'course': courses[0],
            'amount': Decimal('3000.00'),
            'transaction_id': 'TXN001234569',
            'remarks': 'First installment payment.',
            'verified': True,  # One verified payment
            'verified_by': User.objects.filter(role='admin').first(),
            'verification_notes': 'Payment verified and approved. Student enrolled.'
        },
        {
            'student': students[3] if len(students) > 3 else students[0],
            'course': courses[2] if len(courses) > 2 else courses[0],
            'amount': Decimal('4500.00'),
            'transaction_id': 'TXN001234570',
            'remarks': 'Urgent payment for course enrollment.',
            'verified': False
        },
        {
            'student': students[4] if len(students) > 4 else students[1],
            'course': courses[1] if len(courses) > 1 else courses[0],
            'amount': Decimal('6200.00'),
            'transaction_id': 'TXN001234571',
            'remarks': 'Payment via bank transfer.',
            'verified': False
        },
        {
            'student': students[0],
            'course': courses[2] if len(courses) > 2 else courses[0],
            'amount': Decimal('8000.00'),
            'transaction_id': 'TXN001234572',
            'remarks': 'Second course enrollment payment.',
            'verified': True,
            'verified_by': User.objects.filter(role='admin').first(),
            'verification_notes': 'Verified. Good student record.'
        },
    ]
    
    created_count = 0
    for data in test_data:
        payment_method = payment_methods.first()
        
        # Check if already exists
        existing = PaymentVerification.objects.filter(
            user=data['student'],
            course=data['course'],
            transaction_id=data['transaction_id']
        ).first()
        
        if existing:
            print(f"⚠️  Payment already exists: {data['student'].username} - {data['course'].title}")
            continue
        
        # Create payment verification
        payment = PaymentVerification.objects.create(
            user=data['student'],
            course=data['course'],
            payment_method=payment_method,
            amount=data['amount'],
            transaction_id=data['transaction_id'],
            remarks=data['remarks'],
            verified=data['verified']
        )
        
        # Add payment proof image
        payment.payment_proof = create_test_payment_proof()
        payment.save()
        
        # If verified, add verification details
        if data['verified'] and 'verified_by' in data:
            payment.verified_by = data['verified_by']
            payment.verification_notes = data['verification_notes']
            payment.save()
        
        status = "✓ VERIFIED" if payment.verified else "⏳ PENDING"
        print(f"{status} Created: {payment.user.get_full_name()} - {payment.course.title} - ${payment.amount}")
        created_count += 1
    
    print(f"\n{'='*60}")
    print(f"✅ Successfully created {created_count} test payment verifications!")
    print(f"{'='*60}\n")
    
    # Summary
    total = PaymentVerification.objects.count()
    pending = PaymentVerification.objects.filter(verified=False).count()
    verified = PaymentVerification.objects.filter(verified=True).count()
    
    print("📊 SUMMARY:")
    print(f"   Total Payments: {total}")
    print(f"   Pending: {pending}")
    print(f"   Verified: {verified}")
    print("\n🌐 View them at:")
    print("   Admin view: http://localhost:8000/payment-verifications/")
    print("   Student view: http://localhost:8000/payment-verifications/my/")
    print("   Add new: http://localhost:8000/payment-verifications/add/")

if __name__ == '__main__':
    try:
        create_test_data()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
