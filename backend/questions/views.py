from django.db.models import Q
from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from accounts.permissions import IsLecturerOrAdmin
from accounts.models import User
from courses.models import Enrollment
from notifications.models import Notification
from .models import Question
from .serializers import QuestionSerializer, QuestionReadSerializer


class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.select_related("exam")
    serializer_class = QuestionSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_permissions(self):
        if self.action in {"list", "retrieve"}:
            return [permissions.IsAuthenticated()]
        return [IsLecturerOrAdmin()]

    def get_serializer_class(self):
        if self.request.user.role == User.STUDENT and self.action in {"list", "retrieve"}:
            return QuestionReadSerializer
        return QuestionSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        exam_id = self.request.query_params.get("exam")
        if exam_id:
            qs = qs.filter(exam_id=exam_id)
        if self.request.user.role == "ADMIN":
            return qs
        if self.request.user.role == "LECTURER":
            return qs.filter(exam__lecturer=self.request.user)
        return qs.filter(
            status=Question.PUBLISHED,
            exam__status=Question.PUBLISHED,
        ).filter(
            Q(exam__students=self.request.user) | Q(exam__course__enrollments__student=self.request.user)
        ).distinct()

    def perform_create(self, serializer):
        exam = serializer.validated_data.get("exam")
        if self.request.user.role == "LECTURER" and (not exam or exam.lecturer_id != self.request.user.id):
            raise PermissionDenied("You can only add questions to your own examinations.")
        serializer.save()

    @action(detail=True, methods=["post"])
    def publish(self, request, pk=None):
        question = self.get_object()
        if question.status != Question.PUBLISHED:
            question.status = Question.PUBLISHED
            question.save(update_fields=["status"])
            if question.exam_id:
                student_ids = Enrollment.objects.filter(
                    course=question.exam.course, student__role=User.STUDENT
                ).values_list("student_id", flat=True)
                Notification.objects.bulk_create([
                    Notification(
                        user_id=student_id,
                        title=f"New question published: {question.exam.title}",
                        message=f"A new {question.get_question_type_display()} question is available for {question.exam.course.course_code}.",
                    ) for student_id in student_ids
                ])
        return Response(QuestionSerializer(question).data)
