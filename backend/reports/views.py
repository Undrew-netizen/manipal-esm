import csv
from django.http import HttpResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from results.models import Result

class ResultsCsvReportView(APIView):
    permission_classes = (IsAuthenticated,)
    def get(self, request):
        results = Result.objects.select_related("student_exam__student", "student_exam__exam")
        if request.user.role == "STUDENT": results = results.filter(student_exam__student=request.user, published_at__isnull=False)
        elif request.user.role == "LECTURER": results = results.filter(student_exam__exam__lecturer=request.user)
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="results.csv"'
        writer = csv.writer(response); writer.writerow(["Student", "Exam", "Score", "Percentage", "Grade", "Passed"])
        for item in results: writer.writerow([item.student_exam.student.username, item.student_exam.exam.title, item.total_marks, item.percentage, item.grade, item.passed])
        return response
