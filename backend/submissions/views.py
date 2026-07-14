from django.utils import timezone
from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from accounts.permissions import IsLecturerOrAdmin
from .models import Answer, StudentExam
from .serializers import AnswerSerializer, StudentExamSerializer
from .services import grade_student_exam

class StudentExamViewSet(viewsets.ModelViewSet):
    serializer_class = StudentExamSerializer
    permission_classes = (permissions.IsAuthenticated,)
    def get_queryset(self):
        qs = StudentExam.objects.select_related("student", "exam").prefetch_related("answers")
        return qs if self.request.user.role in {"ADMIN", "LECTURER"} else qs.filter(student=self.request.user)
    def perform_create(self, serializer):
        exam = serializer.validated_data["exam"]
        if self.request.user.role != "STUDENT" or exam.status != "PUBLISHED" or not exam.students.filter(pk=self.request.user.pk).exists():
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("This exam is not available to you.")
        serializer.save(student=self.request.user)
    @action(detail=True, methods=["post"])
    def submit(self, request, pk=None):
        attempt = self.get_object(); result = grade_student_exam(attempt); return Response({"result_id": result.id, "score": attempt.score})

class AnswerViewSet(viewsets.ModelViewSet):
    serializer_class = AnswerSerializer
    permission_classes = (permissions.IsAuthenticated,)
    def get_queryset(self):
        qs = Answer.objects.select_related("student_exam", "question")
        return qs if self.request.user.role in {"ADMIN", "LECTURER"} else qs.filter(student_exam__student=self.request.user)
    def perform_create(self, serializer):
        attempt = StudentExam.objects.get(pk=self.request.data["student_exam"], student=self.request.user)
        if serializer.validated_data["question"].exam_id != attempt.exam_id:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({"question": "Question does not belong to this exam."})
        serializer.save(student_exam=attempt)
    @action(detail=True, methods=["post"], permission_classes=[IsLecturerOrAdmin])
    def mark(self, request, pk=None):
        answer = self.get_object(); answer.marks_awarded = request.data.get("marks_awarded", 0); answer.is_marked = True; answer.remarks = request.data.get("remarks", ""); answer.save(); return Response(AnswerSerializer(answer).data)
