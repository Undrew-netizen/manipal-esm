from rest_framework import serializers
from .models import Question
class QuestionSerializer(serializers.ModelSerializer):
    class Meta: model = Question; fields = "__all__"
    def validate_marks(self, value):
        if value <= 0: raise serializers.ValidationError("Marks must be greater than zero.")
        return value
