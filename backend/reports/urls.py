from django.urls import path
from .views import ResultsCsvReportView
urlpatterns = [path("reports/results.csv", ResultsCsvReportView.as_view())]
