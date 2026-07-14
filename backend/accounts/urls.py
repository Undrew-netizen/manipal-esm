from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import AdminUserViewSet, ChangePasswordView, ProfileView, RegisterView

router = DefaultRouter()
router.register("users", AdminUserViewSet, basename="user")
urlpatterns = [path("register/", RegisterView.as_view()), path("profile/", ProfileView.as_view()), path("change-password/", ChangePasswordView.as_view())] + router.urls
