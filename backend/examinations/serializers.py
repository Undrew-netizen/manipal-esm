from rest_framework import serializers
from .models import Exam

class ExamSerializer(serializers.ModelSerializer):
    course_name = serializers.CharField(source="course.course_name", read_only=True)
    class Meta:
        model = Exam
        fields = "__all__"
        read_only_fields = ("lecturer", "status", "created_at", "updated_at")
    def validate(self, attrs):
        start, end = attrs.get("start_time", getattr(self.instance, "start_time", None)), attrs.get("end_time", getattr(self.instance, "end_time", None))
        if start and end and end <= start: raise serializers.ValidationError({"end_time": "End time must be later than start time."})
        return attrs
