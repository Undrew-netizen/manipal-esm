from django.contrib import admin
from .models import Question

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("question", "exam", "question_type", "marks", "difficulty")
    list_filter = ("question_type", "difficulty", "exam")
    search_fields = ("question",)
