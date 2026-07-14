from rest_framework import serializers
from .models import Result

class ResultSerializer(serializers.ModelSerializer):
    exam_title = serializers.CharField(source="student_exam.exam.title", read_only=True)
    course_name = serializers.CharField(source="student_exam.exam.course.course_name", read_only=True)
    class Meta:
        model = Result
        fields = "__all__"
        read_only_fields = "__all__"
