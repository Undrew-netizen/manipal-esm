from django.db.models import Avg
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from accounts.models import User
from courses.models import Course
from departments.models import Department
from examinations.models import Exam
from results.models import Result

class DashboardView(APIView):
    permission_classes = (IsAuthenticated,)
    def get(self, request):
        user = request.user
        if user.role == "STUDENT":
            return Response({"upcoming_exams": Exam.objects.filter(students=user, status=Exam.PUBLISHED).count(), "completed_exams": user.student_exams.exclude(status="IN_PROGRESS").count(), "average_score": user.student_exams.aggregate(value=Avg("score"))["value"], "notifications": user.notifications.filter(read=False).count()})
        if user.role == "LECTURER":
            return Response({"my_courses": user.assigned_courses.count(), "my_exams": user.created_exams.count(), "pending_marking": Result.objects.filter(student_exam__exam__lecturer=user, published_at__isnull=True).count(), "published_results": Result.objects.filter(student_exam__exam__lecturer=user, published_at__isnull=False).count()})
        return Response({"students": User.objects.filter(role="STUDENT").count(), "lecturers": User.objects.filter(role="LECTURER").count(), "departments": Department.objects.count(), "courses": Course.objects.count(), "active_exams": Exam.objects.filter(status=Exam.PUBLISHED).count(), "pass_rate": Result.objects.filter(passed=True).count()})
