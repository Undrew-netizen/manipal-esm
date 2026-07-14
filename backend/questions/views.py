from rest_framework import viewsets
from accounts.permissions import IsLecturerOrAdmin
from .models import Question
from .serializers import QuestionSerializer
class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.select_related("exam")
    serializer_class = QuestionSerializer
    permission_classes = (IsLecturerOrAdmin,)
    def get_queryset(self):
        qs = super().get_queryset()
        return qs if self.request.user.role == "ADMIN" else qs.filter(exam__lecturer=self.request.user)
