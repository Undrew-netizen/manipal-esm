from django.contrib import admin
from .models import Course, Enrollment, Exam, Notification, Profile, Result

admin.site.register([Profile, Course, Enrollment, Exam, Result, Notification])
