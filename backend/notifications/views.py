from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from accounts.models import User
from accounts.permissions import IsAdministrator
from .models import Notification
from .serializers import NotificationSerializer

class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = (permissions.IsAuthenticated,)
    def get_queryset(self): return Notification.objects.filter(user=self.request.user)
    def perform_create(self, serializer): serializer.save(user=self.request.user)

    @action(detail=False, methods=["post"], permission_classes=[IsAdministrator])
    def broadcast(self, request):
        title = str(request.data.get("title", "")).strip()
        message = str(request.data.get("message", "")).strip()
        if not title or not message:
            raise ValidationError({"detail": "A title and message are required."})
        recipients = User.objects.filter(is_active=True)
        role = request.data.get("role")
        user_ids = request.data.get("user_ids")
        if user_ids:
            recipients = recipients.filter(id__in=user_ids)
        elif role in {User.STUDENT, User.LECTURER, User.ADMIN}:
            recipients = recipients.filter(role=role)
        Notification.objects.bulk_create([Notification(user=user, title=title, message=message) for user in recipients])
        return Response({"sent": recipients.count()})
    @action(detail=True, methods=["post"])
    def mark_read(self, request, pk=None):
        notification = self.get_object(); notification.read = True; notification.save(update_fields=["read"])
        return Response(NotificationSerializer(notification).data)
