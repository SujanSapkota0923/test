from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from faker import Faker
import random
from uuid import uuid4
from decimal import Decimal
import io
from PIL import Image

from apps.Course.models import (
    AcademicLevel,
    Stream,
    Subject,
    Enrollment,
    Course,
    LiveClass,
    Video,
)


def gen_image_bytes(format="PNG", size=(200, 120), color=(200, 200, 200)):
    img = Image.new("RGB", size, color=color)
    buf = io.BytesIO()
    img.save(buf, format=format)
    buf.seek(0)
    return buf.read()


def make_file_for_field(name="file"):
    content = gen_image_bytes()
    filename = f"{name}-{uuid4().hex[:6]}.png"
    return SimpleUploadedFile(filename, content, content_type="image/png")


def decimal_for_field(field):
    # create a Decimal value that fits into max_digits and decimal_places
    max_d = getattr(field, "max_digits", 8)
    dec = getattr(field, "decimal_places", 2)
    int_part_digits = max(1, max_d - dec)
    max_int = 10 ** int_part_digits - 1
    val = round(random.uniform(0, min(max_int, 9999)), dec)
    return Decimal(str(val))


def safe_unique(value, field):
    # Append short uuid for unique fields
    if getattr(field, "unique", False):
        return f"{value}-{uuid4().hex[:6]}"
    return value


def truncate(value, field):
    max_len = getattr(field, "max_length", None)
    if max_len and isinstance(value, str):
        return value[:max_len]
    return value


class Command(BaseCommand):
    help = "Populate the database with random test data (students, teachers, levels, subjects, activities, videos, live classes)."

    def add_arguments(self, parser):
        parser.add_argument("--students", type=int, default=20, help="Number of student users to create")
        parser.add_argument("--teachers", type=int, default=5, help="Number of teacher users to create")
        parser.add_argument("--levels", type=int, default=5, help="Number of academic levels to create")
        parser.add_argument("--subjects", type=int, default=10, help="Number of subjects to create")
        parser.add_argument("--activities", type=int, default=5, help="Number of extracurricular activities to create")
        parser.add_argument("--videos", type=int, default=10, help="Number of videos to create")
        parser.add_argument("--liveclasses", type=int, default=8, help="Number of live classes to create")
        parser.add_argument("--fill-all-fields", action="store_true", help="Try to fill every field for selected models")
        parser.add_argument("--fill-count", type=int, default=1, help="How many fully-filled instances to create per selected model when using --fill-all-fields")
        parser.add_argument("--fast", action="store_true", help="Use set_unusable_password for created users to speed up bulk creation")
        parser.add_argument("--seed", type=int, help="Optional random seed for Faker and random")
        parser.add_argument("--force", action="store_true", help="Force running even if DEBUG is False")
        parser.add_argument("--max-retries", type=int, default=3, help="Max retries when validation fails for auto-filled instances")
        parser.add_argument("--models", type=str, help="Comma-separated list of model names to auto-fill (e.g. User,AcademicLevel,Video)")
        parser.add_argument("--no-files", action="store_true", help="Do not create files/images for FileField/ImageField when auto-filling")

    def handle(self, *args, **options):
        seed = options.get("seed")
        if seed:
            Faker.seed(seed)
            random.seed(seed)

        fake = Faker()
        force = options.get("force")
        fill_all = options.get("fill_all_fields")
        no_files = options.get("no_files")
        max_retries = options.get("max_retries") or 3
        models_arg = options.get("models")

        # Safety check: avoid running aggressive filler on non-debug without --force
        if fill_all and not force and not settings.DEBUG:
            self.stdout.write(self.style.ERROR("Refusing to run --fill-all-fields when DEBUG=False. Use --force to override."))
            return
        User = get_user_model()

        students_count = options["students"]
        teachers_count = options["teachers"]
        levels_count = options["levels"]
        subjects_count = options["subjects"]
        activities_count = options["activities"]
        videos_count = options["videos"]
        liveclasses_count = options["liveclasses"]

        self.stdout.write("Starting population of test data...")

        # Academic levels
        levels = []
        for i in range(1, levels_count + 1):
            name = f"Level {i}"
            slug = f"level-{i}"
            level, created = AcademicLevel.objects.get_or_create(
                slug=slug,
                defaults={"name": name, "order": i, "allows_streams": i % 2 == 0, "capacity": random.choice([None, 30, 50])},
            )
            levels.append(level)

        # Streams (for levels that allow streams)
        streams = []
        for level in levels:
            if level.allows_streams:
                for sname in ["Science", "Management"]:
                    slug = f"{level.slug}-{sname.lower()}"
                    stream, _ = Stream.objects.get_or_create(name=sname, slug=slug, level=level)
                    streams.append(stream)

        # Subjects
        subjects = []
        for i in range(subjects_count):
            name = fake.unique.word().capitalize() + f" {i}"
            subject, _ = Subject.objects.get_or_create(name=name, defaults={"description": fake.sentence(6), "levels": random.choice(levels)})
            # attach random streams if available
            if streams and random.random() < 0.4:
                subject.streams.set(random.sample(streams, k=min(len(streams), random.randint(1, 2))))
            subjects.append(subject)

        # Teachers
        teachers = []
        for i in range(teachers_count):
            username = fake.unique.user_name()[:30]
            email = fake.unique.email()
            teacher, created = User.objects.get_or_create(
                username=username,
                defaults={
                    "email": email,
                    "role": User.Role.TEACHER,
                },
            )
            if created:
                if options.get("fast"):
                    teacher.set_unusable_password()
                else:
                    teacher.set_password("test1234")
                teacher.save()
            teachers.append(teacher)

        # Students
        students = []
        for i in range(students_count):
            username = fake.unique.user_name()[:30]
            email = fake.unique.email()
            student, created = User.objects.get_or_create(
                username=username,
                defaults={
                    "email": email,
                    "role": User.Role.STUDENT,
                },
            )
            if created:
                if options.get("fast"):
                    student.set_unusable_password()
                else:
                    student.set_password("test1234")
                student.save()
            students.append(student)

        # Enroll students into random levels (active enrollment)
        for student in students:
            # pick a level that has capacity (or unlimited capacity)
            available_levels = []
            for l in levels:
                if l.capacity is None:
                    available_levels.append(l)
                else:
                    current_active = Enrollment.objects.filter(level=l, is_active=True).count()
                    if current_active < l.capacity:
                        available_levels.append(l)

            if available_levels:
                level = random.choice(available_levels)
                is_active = True
            else:
                # no level has free capacity; pick any level but mark enrollment inactive
                level = random.choice(levels)
                is_active = False

            try:
                enrollment, created = Enrollment.objects.get_or_create(
                    student=student,
                    level=level,
                    defaults={"is_active": is_active, "joined_at": timezone.now()},
                )
            except Exception:
                # fallback: try to create an inactive enrollment or skip
                try:
                    enrollment, created = Enrollment.objects.get_or_create(
                        student=student,
                        level=level,
                        defaults={"is_active": False, "joined_at": timezone.now()},
                    )
                except Exception:
                    continue

            if not created and is_active and not enrollment.is_active:
                # try to activate if possible
                try:
                    enrollment.is_active = True
                    enrollment.save()
                except Exception:
                    pass

        # Courses (previously ExtraCurricularActivity)
        activities = []
        for i in range(activities_count):
            title = fake.sentence(nb_words=4).rstrip('.')
            start = timezone.now() + timezone.timedelta(days=random.randint(1, 30))
            end = start + timezone.timedelta(hours=random.randint(1, 5))
            activity, _ = Course.objects.get_or_create(
                title=title,
                defaults={
                    "description": fake.paragraph(nb_sentences=2),
                    "cost": random.choice([0, 10, 20, 50]),
                    "start_time": start,
                    "end_time": end,
                },
            )
            # add participants
            if students:
                participants = random.sample(students, k=min(len(students), random.randint(0, 5)))
                activity.participants.set(participants)
            activities.append(activity)

        # Videos
        for i in range(videos_count):
            title = fake.sentence(nb_words=5).rstrip('.')
            url = f"https://example.com/video/{uuid4()}"
            video, _ = Video.objects.get_or_create(
                url=url,
                defaults={
                    "title": title,
                    "description": fake.sentence(8),
                    "level": random.choice(levels),
                    "teacher": random.choice(teachers) if teachers else None,
                    "cost": random.choice([0, 5, 10]),
                },
            )

    # Live classes
        for i in range(liveclasses_count):
            title = fake.sentence(nb_words=6).rstrip('.')
            start = timezone.now() + timezone.timedelta(days=random.randint(-2, 5), hours=random.randint(0, 23))
            end = start + timezone.timedelta(hours=1)
            host = random.choice(teachers) if teachers else None
            live, _ = LiveClass.objects.get_or_create(
                title=title + f" {i}",
                defaults={
                    "start_time": start,
                    "end_time": end,
                    "hosts": host,
                    "subject": random.choice(subjects) if subjects else None,
                    "level": random.choice(levels),
                    "course": random.choice(activities) if activities else None,
                },
            )

        # If user requested filling all fields, run auto-filler for listed models
        if fill_all:
            self.stdout.write("Running aggressive auto-fill for fields...")
            # prepare mapping of model name to model class
            model_map = {
                "AcademicLevel": AcademicLevel,
                "Stream": Stream,
                "Subject": Subject,
                "Enrollment": Enrollment,
                "Course": Course,
                "LiveClass": LiveClass,
                "Video": Video,
                "User": get_user_model(),
            }
            selected = list(model_map.keys()) if not models_arg else [m.strip() for m in models_arg.split(",")]
            for name in selected:
                model = model_map.get(name)
                if not model:
                    self.stdout.write(self.style.WARNING(f"Unknown model '{name}' - skipping"))
                    continue
                    # create `fill_count` instances with all fields filled
                    fill_count = options.get("fill_count") or 1
                    successes = 0
                    for idx in range(fill_count):
                        created = self._create_instance_with_all_fields(model, fake, max_retries, no_files=no_files)
                        if created:
                            successes += 1
                            self.stdout.write(self.style.SUCCESS(f"Created {name} (filled) [{idx+1}/{fill_count}]."))
                        else:
                            self.stdout.write(self.style.WARNING(f"Failed to create valid {name} on attempt {idx+1}/{fill_count} after {max_retries} retries."))
                    if successes:
                        self.stdout.write(self.style.SUCCESS(f"Created {successes}/{fill_count} instances of {name} with many fields filled."))

        self.stdout.write(self.style.SUCCESS("Test data population complete."))

    def _create_instance_with_all_fields(self, model, fake, max_retries=3, no_files=False):
        """Attempt to create one instance of `model` with values for most fields.
        Returns the instance on success, or None on repeated failure.
        """
        from django.db import models
        from django.core.exceptions import ValidationError

        def value_for_field(field, instance=None):
            # Skip auto or reverse fields
            if getattr(field, "auto_created", False) or getattr(field, "primary_key", False):
                return None
            # choices
            if getattr(field, "choices", None):
                return random.choice(field.choices)[0]
            # specific types
            cls_name = field.__class__.__name__
            fname = field.name
            if cls_name in ("CharField", "SlugField"):
                v = fake.text(max_nb_chars=min(40, getattr(field, "max_length", 40))).strip()
                if 'email' in fname.lower():
                    v = fake.unique.email()
                if 'username' in fname.lower():
                    v = fake.unique.user_name()[: getattr(field, "max_length", 30)]
                v = safe_unique(v, field)
                return truncate(v, field)
            if cls_name == "TextField":
                return fake.paragraph(nb_sentences=3)
            if cls_name == "BooleanField":
                return random.choice([True, False])
            if cls_name in ("IntegerField", "PositiveIntegerField"):
                if cls_name == "PositiveIntegerField":
                    return random.randint(0, 1000)
                return random.randint(-1000, 1000)
            if cls_name == "DecimalField":
                return decimal_for_field(field)
            if cls_name == "DateTimeField":
                return fake.date_time_between(start_date='-1y', end_date='+1y', tzinfo=timezone.get_current_timezone())
            if cls_name == "DateField":
                return fake.date_between(start_date='-2y', end_date='+1y')
            if cls_name == "EmailField":
                return safe_unique(fake.unique.email(), field)
            if cls_name == "URLField":
                return f"https://example.com/{uuid4().hex}"
            if cls_name == "UUIDField":
                return uuid4()
            if cls_name == "JSONField":
                return {"sample": fake.pydict()}
            if cls_name in ("FileField", "ImageField"):
                if no_files:
                    return None
                return make_file_for_field(fname)
            if cls_name == "ForeignKey":
                rel = field.related_model
                # try to pick an existing object, or create a minimal one
                qs = rel.objects.all()
                if getattr(field, "limit_choices_to", None):
                    try:
                        qs = qs.filter(**field.limit_choices_to)
                    except Exception:
                        pass
                obj = qs.order_by('?').first()
                if obj:
                    return obj
                # Create a minimal related object recursively
                kwargs = {}
                for rf in rel._meta.get_fields():
                    if getattr(rf, "auto_created", False) or getattr(rf, "primary_key", False):
                        continue
                    if rf.many_to_many or rf.one_to_many:
                        continue
                    if rf.is_relation and rf.many_to_one and rf.related_model == model:
                        # avoid circular FK pointing back to this model
                        continue
                    val = value_for_field(rf)
                    if val is not None:
                        kwargs[rf.name] = val
                try:
                    return rel.objects.create(**kwargs)
                except Exception:
                    return None
            # fallback
            return safe_unique(str(uuid4())[:30], field)

        # build kwargs for model
        for attempt in range(max_retries):
            kwargs = {}
            m2m_fields = []
            for field in model._meta.get_fields():
                # Skip reverse relations
                if getattr(field, "auto_created", False) and not getattr(field, "concrete", False):
                    continue
                if field.many_to_many:
                    m2m_fields.append(field)
                    continue
                if field.one_to_many:
                    continue
                val = value_for_field(field)
                if val is not None:
                    # For FK store instance directly
                    kwargs[field.name] = val

            try:
                inst = model.objects.create(**kwargs)
            except Exception as exc:
                # try with full_clean path: create instance then save after full_clean
                try:
                    inst = model(**kwargs)
                    inst.full_clean()
                    inst.save()
                except ValidationError:
                    continue
                except Exception:
                    continue

            # handle m2m
            for m2m in m2m_fields:
                rel = m2m.related_model
                # pick or create a couple related objects
                related_objs = list(rel.objects.all()[:3])
                if not related_objs:
                    # attempt to create one
                    try:
                        ro = rel.objects.create()
                        related_objs = [ro]
                    except Exception:
                        related_objs = []
                try:
                    getattr(inst, m2m.name).set(related_objs)
                except Exception:
                    pass

            # final validation
            try:
                inst.full_clean()
                inst.save()
                return inst
            except ValidationError:
                try:
                    inst.delete()
                except Exception:
                    pass
                continue

        return None
