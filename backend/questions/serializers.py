from rest_framework import serializers
from .models import Question


class QuestionReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = (
            "id",
            "exam",
            "question_type",
            "question",
            "marks",
            "difficulty",
            "image",
            "options",
            "explanation",
        )
        read_only_fields = fields


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = "__all__"
        read_only_fields = ("status",)

    def validate_marks(self, value):
        if value <= 0:
            raise serializers.ValidationError("Marks must be greater than zero.")
        return value

    def validate(self, attrs):
        question_type = attrs.get("question_type", getattr(self.instance, "question_type", None))
        options = attrs.get("options", getattr(self.instance, "options", []))
        correct_answer = attrs.get("correct_answer", getattr(self.instance, "correct_answer", []))
        if question_type == Question.MCQ and len(options) < 2:
            raise serializers.ValidationError({"options": "MCQ questions require at least two options."})
        if question_type == Question.TRUE_FALSE:
            if options and set(options) != {"True", "False"}:
                raise serializers.ValidationError({"options": "True/False options must be True and False."})
            if correct_answer and not set(correct_answer).issubset({"True", "False"}):
                raise serializers.ValidationError({"correct_answer": "Answer must be True or False."})
        if question_type in {Question.ESSAY, Question.SHORT_ANSWER, Question.FILL_BLANK} and options:
            raise serializers.ValidationError({"options": "This question type does not use selectable options."})
        return attrs
