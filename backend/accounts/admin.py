from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

# Register your models here.
@admin.register(User)
class CustomeUserAdmin(UserAdmin):

    fieldsets = UserAdmin.fieldsets + (
        (
            "Additional Information",
            {
                "fields":(
                    "role",
                    "registration_number",
                    "staff_number",
                    "phone",
                    "profile_picture",
                )
            },
        ),
    )

    list_display = (
        "username",
        "email",
        "role",
        "is_staff",
    )

    list_filter =(
        "role",
        "is_staff",
    )

    def has_add_permission(self, request):
        return super().has_add_permission(request) and (request.user.is_superuser or request.user.role == User.ADMIN)

    def has_change_permission(self, request, obj=None):
        return super().has_change_permission(request, obj) and (request.user.is_superuser or request.user.role == User.ADMIN)

    def has_delete_permission(self, request, obj=None):
        return super().has_delete_permission(request, obj) and (request.user.is_superuser or request.user.role == User.ADMIN)
