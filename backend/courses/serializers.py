from rest_framework import serializers
from accounts.models import User
from .models import Course, Enrollment

class CourseSerializer(serializers.ModelSerializer):
    class Meta: model = Course; fields = "__all__"

class EnrollmentSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField(read_only=True)
    course_name = serializers.CharField(source="course.course_name", read_only=True)

    def get_student_name(self, enrollment):
        return enrollment.student.get_full_name() or enrollment.student.username

    class Meta: model = Enrollment; fields = "__all__"

    def validate_student(self, student):
        if student.role != User.STUDENT:
            raise serializers.ValidationError("Only users with the student role can be enrolled in a course.")
        return student
