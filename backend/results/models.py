from django.db import models


class Result(models.Model):
    student_exam = models.OneToOneField("submissions.StudentExam", on_delete=models.CASCADE, related_name="result")
    total_marks = models.DecimalField(max_digits=8, decimal_places=2)
    percentage = models.DecimalField(max_digits=5, decimal_places=2)
    grade = models.CharField(max_length=5)
    passed = models.BooleanField()
    remarks = models.TextField(blank=True)
    published_at = models.DateTimeField(null=True, blank=True)
