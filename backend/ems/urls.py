from django.urls import path
from . import views

urlpatterns = [
    path('auth/register/', views.register),
    path('auth/login/', views.sign_in),
    path('auth/logout/', views.sign_out),
    path('me/', views.me),
    path('dashboard/', views.dashboard),
    path('exams/', views.exams),
    path('results/', views.results),
    path('notifications/', views.notifications),
    path('notifications/<int:notification_id>/read/', views.mark_notification_read),
]
