from django.utils import timezone
from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from accounts.permissions import IsLecturerOrAdmin
from .models import Result
from .serializers import ResultSerializer

class ResultViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ResultSerializer
    permission_classes = (permissions.IsAuthenticated,)
    def get_queryset(self):
        qs = Result.objects.select_related("student_exam__student", "student_exam__exam")
        return qs if self.request.user.role in {"ADMIN", "LECTURER"} else qs.filter(student_exam__student=self.request.user, published_at__isnull=False)
    @action(detail=True, methods=["post"], permission_classes=[IsLecturerOrAdmin])
    def publish(self, request, pk=None):
        result = self.get_object(); result.published_at = timezone.now(); result.save(update_fields=["published_at"])
        return Response(ResultSerializer(result).data)
