from django.contrib import admin
from .models import Answer, StudentExam

@admin.register(StudentExam)
class StudentExamAdmin(admin.ModelAdmin):
    list_display = ("student", "exam", "status", "score", "started_at", "submitted_at")
    list_filter = ("status", "exam")
    search_fields = ("student__username", "exam__title")

@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ("student_exam", "question", "marks_awarded", "is_marked")
    list_filter = ("is_marked",)
