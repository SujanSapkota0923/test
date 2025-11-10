#!/usr/bin/env python3
"""
Create test payment method
"""
import os
import django
import sys

# Setup Django environment
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Course_Management_system.settings')
django.setup()

from apps.Course.models import User, PaymentMethod
import json

# Get admin user
admin = User.objects.filter(role='admin').first()
if not admin:
    print("❌ No admin user found! Please create an admin first.")
    exit(1)

# Create payment methods
payment_methods_data = [
    {
        'name': 'Bank Transfer',
        'description': 'Direct bank transfer to school account',
        'details': json.dumps({
            'bank_name': 'ABC Bank',
            'account_number': '1234567890',
            'account_name': 'School Account',
            'routing_number': '123456'
        }),
        'is_active': True,
        'display_order': 1
    },
    {
        'name': 'Online Payment',
        'description': 'Pay via online payment gateway',
        'details': json.dumps({
            'gateway': 'PaymentGateway',
            'merchant_id': 'SCHOOL123'
        }),
        'is_active': True,
        'display_order': 2
    },
]

print("Creating payment methods...\n")

for pm_data in payment_methods_data:
    pm, created = PaymentMethod.objects.get_or_create(
        name=pm_data['name'],
        defaults={
            'description': pm_data['description'],
            'details': pm_data['details'],
            'is_active': pm_data['is_active'],
            'display_order': pm_data['display_order'],
            'created_by': admin
        }
    )
    
    status = "✓ CREATED" if created else "⚠️  EXISTS"
    print(f"{status}: {pm.name}")

print(f"\n✅ Payment methods ready!")
print(f"Total active payment methods: {PaymentMethod.objects.filter(is_active=True).count()}")
