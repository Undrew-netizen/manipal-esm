from rest_framework import generics, permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from .permissions import IsAdministrator
from .models import User
from .serializers import AdminUserCreateSerializer, ChangePasswordSerializer, RegisterSerializer, UserSerializer


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = (permissions.AllowAny,)


class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    def get_object(self):
        return self.request.user


class ChangePasswordView(APIView):
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if not request.user.check_password(serializer.validated_data["old_password"]):
            return Response({"old_password": ["Incorrect password."]}, status=status.HTTP_400_BAD_REQUEST)
        request.user.set_password(serializer.validated_data["new_password"])
        request.user.save(update_fields=["password"])
        return Response({"detail": "Password changed."})


class AdminUserViewSet(viewsets.ModelViewSet):
    """Administrator-only management of staff accounts."""
    queryset = User.objects.all().select_related("department")
    permission_classes = (IsAdministrator,)

    def get_serializer_class(self):
        return AdminUserCreateSerializer if self.action == "create" else UserSerializer
