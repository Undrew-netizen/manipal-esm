from datetime import date, time
from rest_framework.test import APITestCase
from rest_framework import status
from accounts.models import User
from courses.models import Course
from departments.models import Department
from examinations.models import Exam


class StudentAttemptTests(APITestCase):
    def setUp(self):
        department = Department.objects.create(name="Computing", faculty="Science")
        lecturer = User.objects.create_user(username="lecturer", password="Secur3Password!", role=User.LECTURER, staff_number="S001")
        self.student = User.objects.create_user(username="student", password="Secur3Password!", role=User.STUDENT, registration_number="R001")
        course = Course.objects.create(course_code="CSC101", course_name="Programming", department=department, semester=1, academic_year="2026", assigned_lecturer=lecturer)
        self.exam = Exam.objects.create(title="Test", course=course, lecturer=lecturer, exam_date=date.today(), start_time=time(9), end_time=time(10), duration=60, status=Exam.PUBLISHED)
    def test_student_cannot_start_unassigned_exam(self):
        self.client.force_authenticate(self.student)
        response = self.client.post("/api/student-exams/", {"exam": self.exam.id})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
