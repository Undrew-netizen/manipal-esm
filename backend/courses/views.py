from rest_framework import permissions, viewsets
from accounts.permissions import IsLecturerOrAdmin
from .models import Course, Enrollment
from .serializers import CourseSerializer, EnrollmentSerializer

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.select_related("department", "assigned_lecturer")
    serializer_class = CourseSerializer
    permission_classes = (IsLecturerOrAdmin,)
    def get_queryset(self):
        qs = super().get_queryset()
        return qs if self.request.user.role == "ADMIN" else qs.filter(assigned_lecturer=self.request.user)

class EnrollmentViewSet(viewsets.ModelViewSet):
    serializer_class = EnrollmentSerializer
    permission_classes = (permissions.IsAuthenticated,)
    def get_queryset(self):
        qs = Enrollment.objects.select_related("student", "course")
        return qs if self.request.user.role in {"ADMIN", "LECTURER"} else qs.filter(student=self.request.user)
    def perform_create(self, serializer):
        serializer.save(student=self.request.user if self.request.user.role == "STUDENT" else serializer.validated_data["student"])
