from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from results.models import Result
from .models import StudentExam

def grade_student_exam(student_exam: StudentExam):
    answers = student_exam.answers.select_related("question")
    score = sum((answer.marks_awarded for answer in answers), Decimal("0"))
    total = sum((answer.question.marks for answer in answers), Decimal("0"))
    percentage = (score / total * 100) if total else Decimal("0")
    grade = "A" if percentage >= 80 else "B" if percentage >= 70 else "C" if percentage >= 60 else "D" if percentage >= 50 else "F"
    student_exam.score = score; student_exam.status = StudentExam.SUBMITTED; student_exam.submitted_at = timezone.now(); student_exam.save()
    return Result.objects.update_or_create(student_exam=student_exam, defaults={"total_marks": score, "percentage": percentage, "grade": grade, "passed": score >= student_exam.exam.passing_marks})[0]
