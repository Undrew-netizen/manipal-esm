from django.contrib import admin
from .models import Result

@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ("student_exam", "total_marks", "percentage", "grade", "passed", "published_at")
    list_filter = ("passed", "grade", "published_at")
