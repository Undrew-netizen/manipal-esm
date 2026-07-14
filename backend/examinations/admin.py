from django.contrib import admin
from .models import Exam

@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "lecturer", "exam_date", "start_time", "status")
    list_filter = ("status", "exam_date", "course")
    search_fields = ("title", "course__course_code")
    filter_horizontal = ("students",)
