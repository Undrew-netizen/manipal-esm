from rest_framework.routers import DefaultRouter
from .views import AnswerViewSet, StudentExamViewSet
router = DefaultRouter(); router.register("student-exams", StudentExamViewSet, basename="student-exam"); router.register("answers", AnswerViewSet, basename="answer")
urlpatterns = router.urls
