from django.conf import settings
from django.db import models


class StudentExam(models.Model):
    IN_PROGRESS, SUBMITTED, AUTO_SUBMITTED = "IN_PROGRESS", "SUBMITTED", "AUTO_SUBMITTED"
    STATUS_CHOICES = ((IN_PROGRESS, "In progress"), (SUBMITTED, "Submitted"), (AUTO_SUBMITTED, "Auto submitted"))
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="student_exams")
    exam = models.ForeignKey("examinations.Exam", on_delete=models.CASCADE, related_name="student_exams")
    started_at = models.DateTimeField(auto_now_add=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=IN_PROGRESS)
    score = models.DecimalField(max_digits=8, decimal_places=2, default=0)

    class Meta:
        constraints = [models.UniqueConstraint(fields=("student", "exam"), name="student_exam_unique")]


class Answer(models.Model):
    student_exam = models.ForeignKey(StudentExam, on_delete=models.CASCADE, related_name="answers")
    question = models.ForeignKey("questions.Question", on_delete=models.CASCADE, related_name="answers")
    student_answer = models.JSONField(default=dict, blank=True)
    marks_awarded = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    is_marked = models.BooleanField(default=False)
    remarks = models.TextField(blank=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=("student_exam", "question"), name="student_exam_question_unique")]
