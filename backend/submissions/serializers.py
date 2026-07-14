from rest_framework import serializers
from .models import Answer, StudentExam

class AnswerSerializer(serializers.ModelSerializer):
    class Meta: model = Answer; fields = "__all__"; read_only_fields = ("student_exam", "marks_awarded", "is_marked")

class StudentExamSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True, read_only=True)
    student_name = serializers.CharField(source="student.username", read_only=True)
    exam_title = serializers.CharField(source="exam.title", read_only=True)
    class Meta: model = StudentExam; fields = "__all__"; read_only_fields = ("student", "started_at", "submitted_at", "status", "score")
