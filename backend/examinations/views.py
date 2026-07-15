from django.db import models
from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from accounts.permissions import IsLecturerOrAdmin
from accounts.models import User
from courses.models import Enrollment
from notifications.models import Notification
from questions.models import Question
from .models import Exam
from .serializers import ExamSerializer

class ExamViewSet(viewsets.ModelViewSet):
    serializer_class = ExamSerializer
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Exam.objects.select_related("course", "lecturer").prefetch_related("students")
    def get_permissions(self):
        if self.action in {"list", "retrieve"}:
            return [permissions.IsAuthenticated()]
        return [IsLecturerOrAdmin()]
    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.role == "ADMIN": return qs
        if self.request.user.role == "LECTURER": return qs.filter(lecturer=self.request.user)
        return qs.filter(status=Exam.PUBLISHED).filter(
            models.Q(students=self.request.user) | models.Q(course__enrollments__student=self.request.user)
        ).distinct()

    def perform_create(self, serializer):
        course = serializer.validated_data["course"]
        if self.request.user.role == User.LECTURER and course.assigned_lecturer_id != self.request.user.id:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You can only create exams for courses assigned to you.")
        serializer.save(lecturer=self.request.user)
    def create(self, request, *args, **kwargs):
        if request.user.role not in {"ADMIN", "LECTURER"}:
            return Response({"detail": "Lecturer access required."}, status=403)
        return super().create(request, *args, **kwargs)
    @action(detail=True, methods=["post"])
    def publish(self, request, pk=None):
        exam = self.get_object()
        if exam.status != Exam.PUBLISHED:
            exam.questions.filter(status=Question.DRAFT).update(status=Question.PUBLISHED)
            enrolled_student_ids = Enrollment.objects.filter(course=exam.course, student__role=User.STUDENT).values_list("student_id", flat=True)
            assigned_student_ids = exam.students.filter(role=User.STUDENT).values_list("id", flat=True)
            student_ids = set(enrolled_student_ids).union(assigned_student_ids)
            Notification.objects.bulk_create([
                Notification(
                    user_id=student_id,
                    title=f"New exam published: {exam.title}",
                    message=(f"{exam.course.course_code} - {exam.course.course_name}: "
                             f"{exam.exam_date} from {exam.start_time} to {exam.end_time}."),
                )
                for student_id in student_ids
            ])
            exam.status = Exam.PUBLISHED
            exam.save(update_fields=["status"])
        return Response(ExamSerializer(exam).data)
    @action(detail=True, methods=["post"])
    def close(self, request, pk=None):
        exam = self.get_object(); exam.status = Exam.CLOSED; exam.save(update_fields=["status"]); return Response(ExamSerializer(exam).data)
    @action(detail=True, methods=["post"])
    def assign_students(self, request, pk=None):
        exam = self.get_object(); exam.students.set(request.data.get("student_ids", [])); return Response(ExamSerializer(exam).data)
