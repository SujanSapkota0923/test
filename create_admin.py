#!/usr/bin/env python3
"""
Create admin user with username 'a' and password 'a'
"""
import os
import django
import sys

# Setup Django environment
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Course_Management_system.settings')
django.setup()

from apps.Course.models import User

# Delete existing user if any
try:
    User.objects.filter(username='a').delete()
except Exception as e:
    print(f"Note: {e}")

# Create admin user
try:
    admin = User.objects.create_superuser(
        username='a',
        email='a@admin.com',
        password='a',
        first_name='Admin',
        last_name='User'
    )
except Exception as e:
    # User might already exist, try to get it
    admin = User.objects.get(username='a')
    print(f"Note: User 'a' already exists")

print("=" * 60)
print("✅ Admin user created successfully!")
print("=" * 60)
print(f"Username: a")
print(f"Password: a")
print(f"Email: a@admin.com")
print(f"Role: {admin.role}")
print(f"Is Staff: {admin.is_staff}")
print(f"Is Superuser: {admin.is_superuser}")
print("=" * 60)
print("\n🌐 Login at: http://localhost:8000/login/")
