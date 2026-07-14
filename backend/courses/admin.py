from django.contrib import admin
from .models import Course, Enrollment

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("course_code", "course_name", "department", "semester", "academic_year", "assigned_lecturer")
    list_filter = ("department", "semester", "academic_year")
    search_fields = ("course_code", "course_name")

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("student", "course", "enrolled_at")
    list_filter = ("course",)
    search_fields = ("student__username", "course__course_code")
