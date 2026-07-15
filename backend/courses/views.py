from rest_framework import permissions, viewsets
from rest_framework.exceptions import PermissionDenied
from accounts.permissions import IsLecturerOrAdmin
from .models import Course, Enrollment
from .serializers import CourseSerializer, EnrollmentSerializer

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.select_related("department", "assigned_lecturer")
    serializer_class = CourseSerializer
    permission_classes = (permissions.IsAuthenticated,)
    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.role == "ADMIN":
            return qs
        if self.request.user.role == "LECTURER":
            return qs.filter(assigned_lecturer=self.request.user)
        return qs.filter(enrollments__student=self.request.user).distinct()

    def get_permissions(self):
        if self.action in {"list", "retrieve"}:
            return [permissions.IsAuthenticated()]
        return [IsLecturerOrAdmin()]

class EnrollmentViewSet(viewsets.ModelViewSet):
    serializer_class = EnrollmentSerializer
    permission_classes = (permissions.IsAuthenticated,)
    def get_queryset(self):
        qs = Enrollment.objects.select_related("student", "course")
        if self.request.user.role == "ADMIN":
            return qs
        if self.request.user.role == "LECTURER":
            return qs.filter(course__assigned_lecturer=self.request.user)
        return qs.filter(student=self.request.user)
    def perform_create(self, serializer):
        if self.request.user.role == "STUDENT":
            serializer.save(student=self.request.user)
            return
        if self.request.user.role == "ADMIN":
            serializer.save()
            return
        raise PermissionDenied("Only administrators may enrol students in a course.")
