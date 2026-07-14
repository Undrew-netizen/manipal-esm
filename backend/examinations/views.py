from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from accounts.permissions import IsLecturerOrAdmin
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
        return qs.filter(students=self.request.user, status=Exam.PUBLISHED)
    def perform_create(self, serializer): serializer.save(lecturer=self.request.user)
    def create(self, request, *args, **kwargs):
        if request.user.role not in {"ADMIN", "LECTURER"}:
            return Response({"detail": "Lecturer access required."}, status=403)
        return super().create(request, *args, **kwargs)
    @action(detail=True, methods=["post"])
    def publish(self, request, pk=None):
        exam = self.get_object(); exam.status = Exam.PUBLISHED; exam.save(update_fields=["status"]); return Response(ExamSerializer(exam).data)
    @action(detail=True, methods=["post"])
    def close(self, request, pk=None):
        exam = self.get_object(); exam.status = Exam.CLOSED; exam.save(update_fields=["status"]); return Response(ExamSerializer(exam).data)
    @action(detail=True, methods=["post"])
    def assign_students(self, request, pk=None):
        exam = self.get_object(); exam.students.set(request.data.get("student_ids", [])); return Response(ExamSerializer(exam).data)
