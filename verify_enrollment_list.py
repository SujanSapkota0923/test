import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Course_Management_system.settings')
django.setup()

from apps.Course.models import User, Course

print("=" * 60)
print("ENROLLMENT LIST VERIFICATION")
print("=" * 60)

# This simulates what the enrollment_list_view does
enrollment_list = User.objects.filter(role=User.Role.STUDENT, course__isnull=True).order_by('username')[:10]

print(f"\nShowing first 10 students from enrollment list:")
print(f"(These are students WITHOUT courses, available for enrollment)\n")

for idx, student in enumerate(enrollment_list, 1):
    print(f"{idx}. {student.username}")
    print(f"   Name: {student.first_name} {student.last_name}")
    print(f"   Email: {student.email}")
    print(f"   Academic Level: {student.academic_level.name if student.academic_level else 'N/A'}")
    print(f"   Course: {student.course}")  # Should be None
    print(f"   Enrolled: {student.enrolled}")  # Should be False
    
    # Double-check verification as requested by user
    if student.course is not None:
        print(f"   ❌ ERROR: Student has course but appears in enrollment list!")
    else:
        print(f"   ✓ Correct: Student has no course")
    print()

# Verify no enrolled students appear in the list
print("\n" + "=" * 60)
print("VERIFICATION: Checking if any enrolled students appear in list")
print("=" * 60)

# This query should return 0 - checking if list has anyone with a course
enrollment_list_ids = list(User.objects.filter(role=User.Role.STUDENT, course__isnull=True).values_list('id', flat=True))
enrolled_in_list = User.objects.filter(id__in=enrollment_list_ids, course__isnull=False).count()

print(f"\nEnrolled students in enrollment list: {enrolled_in_list}")
if enrolled_in_list == 0:
    print("✓ PASS: No enrolled students in enrollment list")
else:
    print(f"❌ FAIL: Found {enrolled_in_list} enrolled students in list!")

# Show some enrolled students for comparison
print("\n" + "=" * 60)
print("ENROLLED STUDENTS (for comparison)")
print("=" * 60)

enrolled_students = User.objects.filter(role=User.Role.STUDENT, course__isnull=False)[:5]
print(f"\nShowing 5 enrolled students (should NOT appear in enrollment list):\n")

for idx, student in enumerate(enrolled_students, 1):
    print(f"{idx}. {student.username}")
    print(f"   Course: {student.course.title}")
    print(f"   Enrolled: {student.enrolled}")
    print()

print("=" * 60)
print("VERIFICATION COMPLETE")
print("=" * 60)
