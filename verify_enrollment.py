import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Course_Management_system.settings')
django.setup()

from apps.Course.models import User

# Check total students
total_students = User.objects.filter(role=User.Role.STUDENT).count()
print(f"Total students: {total_students}")

# Check students with courses (enrolled)
enrolled_students = User.objects.filter(role=User.Role.STUDENT, course__isnull=False).count()
print(f"Students with courses (enrolled): {enrolled_students}")

# Check students without courses (available for enrollment)
available_students = User.objects.filter(role=User.Role.STUDENT, course__isnull=True).count()
print(f"Students without courses (available for enrollment): {available_students}")

# List a few students with courses
print("\nSample enrolled students:")
for student in User.objects.filter(role=User.Role.STUDENT, course__isnull=False)[:5]:
    print(f"  - {student.username} ({student.first_name} {student.last_name}): enrolled={student.enrolled}, course={student.course.title if student.course else 'None'}")

# List a few students without courses
print("\nSample students available for enrollment:")
for student in User.objects.filter(role=User.Role.STUDENT, course__isnull=True)[:5]:
    print(f"  - {student.username} ({student.first_name} {student.last_name}): enrolled={student.enrolled}, course={student.course}")

print("\n✓ Verification complete!")
