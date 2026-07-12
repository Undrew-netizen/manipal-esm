import json

from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone

from .models import Course, Enrollment, Exam, Profile, Result


class AuthenticationApiTests(TestCase):
    def test_student_registration_logs_in_and_returns_dashboard(self):
        response = self.client.post(
            '/api/auth/register/',
            data=json.dumps({
                'username': 'aarav', 'password': 'safe-test-password',
                'email': 'aarav@example.com', 'identifier': '230911104',
            }),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()['user']['role'], 'student')

        dashboard = self.client.get('/api/dashboard/')
        self.assertEqual(dashboard.status_code, 200)
        self.assertEqual(dashboard.json()['role'], 'student')

    def test_frontend_is_available_from_django(self):
        response = self.client.get('/login.html')
        self.assertEqual(response.status_code, 200)

    def test_student_only_receives_published_own_results(self):
        student = User.objects.create_user('student', password='test-password')
        Profile.objects.create(user=student, identifier='STU-001', role=Profile.Role.STUDENT)
        lecturer = User.objects.create_user('lecturer', password='test-password')
        Profile.objects.create(user=lecturer, identifier='LEC-001', role=Profile.Role.LECTURER)
        course = Course.objects.create(code='CSE201', title='Data Structures', department='CSE', lecturer=lecturer)
        Enrollment.objects.create(student=student, course=course)
        published_exam = Exam.objects.create(course=course, title='Published Exam', starts_at=timezone.now(), venue='Hall A', status=Exam.Status.PUBLISHED)
        hidden_exam = Exam.objects.create(course=course, title='Hidden Exam', starts_at=timezone.now(), venue='Hall A', status=Exam.Status.PUBLISHED)
        Result.objects.create(exam=published_exam, student=student, total_marks=81, grade='A', semester=4, published=True)
        Result.objects.create(exam=hidden_exam, student=student, total_marks=50, grade='B', semester=4, published=False)

        self.client.force_login(student)
        response = self.client.get('/api/results/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()['results']), 1)
        self.assertEqual(response.json()['results'][0]['exam'], 'Published Exam')
