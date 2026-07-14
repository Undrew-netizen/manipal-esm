from rest_framework.test import APITestCase
from rest_framework import status
from .models import User


class AuthenticationApiTests(APITestCase):
    def test_student_can_register_and_obtain_a_token(self):
        response = self.client.post("/api/register/", {"username": "student1", "email": "student@example.com", "password": "Secur3Password!", "role": "STUDENT", "registration_number": "REG001"})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.client.post("/api/token/", {"username": "student1", "password": "Secur3Password!"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)

    def test_public_registration_cannot_create_an_administrator(self):
        response = self.client.post("/api/register/", {"username": "admin1", "password": "Secur3Password!", "role": "ADMIN"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(User.objects.filter(username="admin1").exists())

    def test_public_registration_cannot_create_a_lecturer(self):
        response = self.client.post("/api/register/", {"username": "lecturer1", "password": "Secur3Password!", "role": "LECTURER", "staff_number": "S001"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(User.objects.filter(username="lecturer1").exists())
