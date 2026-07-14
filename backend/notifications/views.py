from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Notification
from .serializers import NotificationSerializer

class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = (permissions.IsAuthenticated,)
    def get_queryset(self): return Notification.objects.filter(user=self.request.user)
    def perform_create(self, serializer): serializer.save(user=self.request.user)
    @action(detail=True, methods=["post"])
    def mark_read(self, request, pk=None):
        notification = self.get_object(); notification.read = True; notification.save(update_fields=["read"])
        return Response(NotificationSerializer(notification).data)
