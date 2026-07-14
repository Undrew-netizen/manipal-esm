from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class Exam(models.Model):
    DRAFT, PUBLISHED, CLOSED = "DRAFT", "PUBLISHED", "CLOSED"
    STATUS_CHOICES = ((DRAFT, "Draft"), (PUBLISHED, "Published"), (CLOSED, "Closed"))
    title = models.CharField(max_length=200)
    course = models.ForeignKey("courses.Course", on_delete=models.PROTECT, related_name="exams")
    lecturer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="created_exams")
    instructions = models.TextField(blank=True)
    exam_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    duration = models.PositiveIntegerField(help_text="Duration in minutes")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=DRAFT)
    passing_marks = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    students = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name="assigned_exams")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-exam_date", "start_time")

    def clean(self):
        if self.end_time <= self.start_time:
            raise ValidationError({"end_time": "End time must be later than start time."})

    def __str__(self):
        return self.title
