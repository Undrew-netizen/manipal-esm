from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "email", "first_name", "last_name", "role", "registration_number", "staff_number", "phone", "profile_picture", "department")
        read_only_fields = ("role",)


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    class Meta:
        model = User
        fields = ("username", "email", "password", "first_name", "last_name", "role", "registration_number", "staff_number", "phone", "department", "profile_picture")
    def validate(self, attrs):
        if attrs["role"] != User.STUDENT:
            raise serializers.ValidationError({"role": "Public registration is limited to students."})
        if attrs["role"] == User.STUDENT and not attrs.get("registration_number"):
            raise serializers.ValidationError({"registration_number": "Required for students."})
        if attrs["role"] == User.LECTURER and not attrs.get("staff_number"):
            raise serializers.ValidationError({"staff_number": "Required for lecturers."})
        return attrs
    def create(self, validated_data):
        password = validated_data.pop("password")
        return User.objects.create_user(password=password, **validated_data)


class AdminUserCreateSerializer(serializers.ModelSerializer):
    """Used only by administrators to create lecturer or administrator accounts."""
    password = serializers.CharField(write_only=True, validators=[validate_password])

    class Meta:
        model = User
        fields = ("username", "email", "password", "first_name", "last_name", "role", "registration_number", "staff_number", "phone", "department")

    def validate(self, attrs):
        if attrs["role"] == User.STUDENT:
            raise serializers.ValidationError({"role": "Student accounts must use the public registration endpoint."})
        if attrs["role"] == User.LECTURER and not attrs.get("staff_number"):
            raise serializers.ValidationError({"staff_number": "Required for lecturers."})
        return attrs

    def create(self, validated_data):
        password = validated_data.pop("password")
        return User.objects.create_user(password=password, **validated_data)


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, validators=[validate_password])
