from django.core.exceptions import ValidationError
from django.db import models


class Question(models.Model):
    MCQ, ESSAY, TRUE_FALSE, FILL_BLANK, SHORT_ANSWER, MATCHING = "MCQ", "ESSAY", "TRUE_FALSE", "FILL_BLANK", "SHORT_ANSWER", "MATCHING"
    TYPES = ((MCQ, "MCQ"), (ESSAY, "Essay"), (TRUE_FALSE, "True/False"), (FILL_BLANK, "Fill blank"), (SHORT_ANSWER, "Short answer"), (MATCHING, "Matching"))
    DRAFT, PUBLISHED = "DRAFT", "PUBLISHED"
    STATUS_CHOICES = ((DRAFT, "Draft"), (PUBLISHED, "Published"))
    exam = models.ForeignKey("examinations.Exam", on_delete=models.CASCADE, related_name="questions", null=True, blank=True)
    question_type = models.CharField(max_length=20, choices=TYPES, default=MCQ)
    question = models.TextField()
    marks = models.DecimalField(max_digits=7, decimal_places=2)
    difficulty = models.CharField(max_length=20, blank=True)
    image = models.ImageField(upload_to="questions/", null=True, blank=True)
    options = models.JSONField(default=list, blank=True)
    correct_answer = models.JSONField(default=list, blank=True)
    explanation = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=DRAFT)

    def clean(self):
        if self.marks <= 0:
            raise ValidationError({"marks": "Marks must be greater than zero."})
