from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.
class User(AbstractUser):
    ADMIN ="ADMIN"
    LECTURER= "LECTURER"
    STUDENT = "STUDENT"

    ROLE_CHOICES = [
        (ADMIN, "Administrator"),
        (LECTURER, "lecturer"),
        (STUDENT, "student"),
    ]

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default=STUDENT
    )

    registration_number = models.CharField(
        max_length=30,
        blank=True,
        null=True,
        unique=True
    )

    staff_number = models.CharField(
        max_length=30,
        blank=True,
        null=True,
        unique=True
    )

    profile_picture = models.ImageField(
        upload_to="profiles/",
        blank=True,
        null=True
    )
    phone = models.CharField(max_length=30, blank=True)
    department = models.ForeignKey(
        "departments.Department", on_delete=models.SET_NULL,
        null=True, blank=True, related_name="users"
    )

    def __str__(self):
        return self.username
