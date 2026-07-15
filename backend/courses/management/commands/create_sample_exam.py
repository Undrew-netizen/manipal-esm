from django.core.management.base import BaseCommand
from django.utils import timezone
from accounts.models import User
from courses.models import Course, Enrollment
from departments.models import Department
from examinations.models import Exam
from questions.models import Question


class Command(BaseCommand):
    help = 'Create a sample Software Engineering course, enroll students, assign a lecturer, and create a published exam with questions.'

    def handle(self, *args, **options):
        department, _ = Department.objects.get_or_create(
            name='Software Engineering',
            defaults={'faculty': 'Engineering', 'description': 'Software Engineering department.'}
        )

        lecturer, _ = User.objects.get_or_create(
            username='se_lecturer',
            defaults={
                'email': 'se_lecturer@example.com',
                'first_name': 'Sarah',
                'last_name': 'Khan',
                'role': User.LECTURER,
                'staff_number': 'LEC100',
                'department': department,
            },
        )
        if lecturer.pk and not lecturer.has_usable_password():
            lecturer.set_password('Lecturer123!')
            lecturer.save(update_fields=['password'])

        course, _ = Course.objects.get_or_create(
            course_code='SE101',
            defaults={
                'course_name': 'Software Engineering',
                'department': department,
                'semester': 1,
                'academic_year': '2026',
                'assigned_lecturer': lecturer,
            },
        )

        student_usernames = ['se_student1', 'se_student2']
        for username in student_usernames:
            student, _ = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': f'{username}@example.com',
                    'first_name': 'Sample',
                    'last_name': 'Student',
                    'role': User.STUDENT,
                    'registration_number': f'R{username[-1]}001',
                    'department': department,
                },
            )
            if student.pk and not student.has_usable_password():
                student.set_password('Student123!')
                student.save(update_fields=['password'])
            Enrollment.objects.get_or_create(student=student, course=course)

        exam, created = Exam.objects.get_or_create(
            title='Software Engineering Midterm',
            course=course,
            lecturer=lecturer,
            defaults={
                'instructions': 'Answer all questions. This exam covers requirements engineering, design, and testing.',
                'exam_date': timezone.now().date(),
                'start_time': timezone.now().time().replace(hour=9, minute=0, second=0, microsecond=0),
                'end_time': timezone.now().time().replace(hour=10, minute=0, second=0, microsecond=0),
                'duration': 60,
                'status': Exam.PUBLISHED,
                'passing_marks': 40,
            },
        )

        if created or not exam.questions.exists():
            Question.objects.filter(exam=exam).delete()
            Question.objects.create(
                exam=exam,
                question_type=Question.MCQ,
                question='Which software development lifecycle model is most associated with sequential phases?',
                marks=5,
                options=['Waterfall', 'Agile', 'Spiral', 'DevOps'],
                correct_answer=['Waterfall'],
                status=Question.PUBLISHED,
            )
            Question.objects.create(
                exam=exam,
                question_type=Question.TRUE_FALSE,
                question='The primary goal of requirements engineering is to understand stakeholder needs.',
                marks=5,
                options=['True', 'False'],
                correct_answer=['True'],
                status=Question.PUBLISHED,
            )
            Question.objects.create(
                exam=exam,
                question_type=Question.ESSAY,
                question='Describe two advantages of using agile methodologies for software development.',
                marks=10,
                correct_answer=[''],
                status=Question.PUBLISHED,
            )

        self.stdout.write(self.style.SUCCESS('Sample Software Engineering course, users, exam, and questions created.'))
