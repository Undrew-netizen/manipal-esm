from django.conf import settings
from django.db import models


class Course(models.Model):
    course_code = models.CharField(max_length=30, unique=True)
    course_name = models.CharField(max_length=200)
    department = models.ForeignKey("departments.Department", on_delete=models.PROTECT, related_name="courses")
    semester = models.PositiveSmallIntegerField()
    academic_year = models.CharField(max_length=20)
    assigned_lecturer = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="assigned_courses")

    class Meta:
        ordering = ("course_code",)
        constraints = [models.UniqueConstraint(fields=("course_code", "academic_year"), name="course_year_unique")]

    def __str__(self):
        return f"{self.course_code} — {self.course_name}"


class Enrollment(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="enrollments")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="enrollments")
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=("student", "course"), name="student_course_unique")]
