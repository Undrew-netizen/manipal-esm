import json
import mimetypes
from functools import wraps

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db.models import Count, Q
from django.http import JsonResponse
from django.http import FileResponse, Http404
from django.conf import settings
from django.utils.dateparse import parse_datetime
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .models import Course, Enrollment, Exam, Notification, Profile, Result


def payload(request):
    try:
        return json.loads(request.body or '{}')
    except json.JSONDecodeError:
        return None


def error(message, status=400):
    return JsonResponse({'detail': message}, status=status)


def profile_data(user):
    profile, _ = Profile.objects.get_or_create(user=user, defaults={'identifier': user.username})
    return {
        'id': user.id, 'username': user.username, 'name': user.get_full_name() or user.username,
        'email': user.email, 'role': profile.role, 'identifier': profile.identifier,
        'department': profile.department, 'programme': profile.programme, 'semester': profile.semester,
    }


def authenticated(view):
    @wraps(view)
    def wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return error('Authentication required.', 401)
        return view(request, *args, **kwargs)
    return wrapped


def roles(*allowed):
    def decorator(view):
        @wraps(view)
        def wrapped(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return error('Authentication required.', 401)
            if profile_data(request.user)['role'] not in allowed:
                return error('You do not have permission for this action.', 403)
            return view(request, *args, **kwargs)
        return wrapped
    return decorator


def exam_data(exam):
    return {
        'id': exam.id, 'title': exam.title, 'course': {'id': exam.course_id, 'code': exam.course.code, 'title': exam.course.title},
        'starts_at': exam.starts_at.isoformat(), 'duration_minutes': exam.duration_minutes, 'venue': exam.venue,
        'instructions': exam.instructions, 'status': exam.status,
    }


def result_data(result):
    return {
        'id': result.id, 'exam_id': result.exam_id, 'exam': result.exam.title, 'course': result.exam.course.code,
        'student': profile_data(result.student), 'internal_marks': result.internal_marks,
        'exam_marks': result.exam_marks, 'total_marks': result.total_marks, 'grade': result.grade,
        'semester': result.semester, 'published': result.published,
    }


@csrf_exempt
@require_http_methods(['POST'])
def register(request):
    data = payload(request)
    if data is None:
        return error('Invalid JSON body.')
    required = ('username', 'password', 'email', 'identifier')
    if any(not data.get(field) for field in required):
        return error('username, password, email, and identifier are required.')
    if User.objects.filter(username=data['username']).exists() or Profile.objects.filter(identifier=data['identifier']).exists():
        return error('Username or identifier is already in use.', 409)
    user = User.objects.create_user(username=data['username'], password=data['password'], email=data['email'], first_name=data.get('first_name', ''), last_name=data.get('last_name', ''))
    Profile.objects.create(user=user, identifier=data['identifier'], role=Profile.Role.STUDENT, programme=data.get('programme', ''), semester=data.get('semester') or None)
    login(request, user)
    return JsonResponse({'user': profile_data(user)}, status=201)


@csrf_exempt
@require_http_methods(['POST'])
def sign_in(request):
    data = payload(request)
    if data is None:
        return error('Invalid JSON body.')
    user = authenticate(request, username=data.get('username', ''), password=data.get('password', ''))
    if user is None:
        return error('Invalid username or password.', 401)
    login(request, user)
    return JsonResponse({'user': profile_data(user)})


@csrf_exempt
@require_http_methods(['POST'])
def sign_out(request):
    logout(request)
    return JsonResponse({'detail': 'Signed out.'})


@authenticated
@require_http_methods(['GET', 'PATCH'])
def me(request):
    if request.method == 'GET':
        return JsonResponse({'user': profile_data(request.user)})
    data = payload(request)
    if data is None:
        return error('Invalid JSON body.')
    user, profile = request.user, request.user.profile
    for field in ('first_name', 'last_name', 'email'):
        if field in data:
            setattr(user, field, data[field])
    user.save()
    for field in ('department', 'programme', 'semester'):
        if field in data:
            setattr(profile, field, data[field])
    profile.save()
    return JsonResponse({'user': profile_data(user)})


@authenticated
@require_http_methods(['GET'])
def dashboard(request):
    role = profile_data(request.user)['role']
    if role == Profile.Role.STUDENT:
        exams = Exam.objects.filter(course__enrollments__student=request.user, status=Exam.Status.PUBLISHED).distinct()
        return JsonResponse({'role': role, 'summary': {'upcoming_exams': exams.count(), 'published_results': Result.objects.filter(student=request.user, published=True).count(), 'unread_notifications': request.user.notifications.filter(is_read=False).count()}, 'upcoming_exams': [exam_data(e) for e in exams[:5]]})
    if role == Profile.Role.LECTURER:
        exams = Exam.objects.filter(Q(course__lecturer=request.user) | Q(created_by=request.user)).distinct()
        return JsonResponse({'role': role, 'summary': {'courses': request.user.courses.count(), 'scheduled_exams': exams.count(), 'pending_grading': Result.objects.filter(exam__in=exams, published=False).count(), 'students': Enrollment.objects.filter(course__in=request.user.courses.all()).values('student').distinct().count()}, 'upcoming_exams': [exam_data(e) for e in exams[:5]]})
    return JsonResponse({'role': role, 'summary': {'students': Profile.objects.filter(role=Profile.Role.STUDENT).count(), 'lecturers': Profile.objects.filter(role=Profile.Role.LECTURER).count(), 'exams': Exam.objects.count(), 'published_results': Result.objects.filter(published=True).count()}})


@authenticated
@require_http_methods(['GET', 'POST'])
def exams(request):
    role = profile_data(request.user)['role']
    if request.method == 'GET':
        query = Exam.objects.select_related('course')
        if role == Profile.Role.STUDENT:
            query = query.filter(course__enrollments__student=request.user, status=Exam.Status.PUBLISHED).distinct()
        elif role == Profile.Role.LECTURER:
            query = query.filter(Q(course__lecturer=request.user) | Q(created_by=request.user)).distinct()
        return JsonResponse({'exams': [exam_data(item) for item in query]})
    if role not in (Profile.Role.LECTURER, Profile.Role.ADMIN):
        return error('Only lecturers and administrators can create exams.', 403)
    data = payload(request)
    if data is None or not all(data.get(key) for key in ('course_id', 'title', 'starts_at', 'venue')):
        return error('course_id, title, starts_at, and venue are required.')
    try:
        course = Course.objects.get(pk=data['course_id'])
    except Course.DoesNotExist:
        return error('Course not found.', 404)
    if role == Profile.Role.LECTURER and course.lecturer_id != request.user.id:
        return error('You can only create exams for your courses.', 403)
    starts_at = parse_datetime(data['starts_at'])
    if starts_at is None:
        return error('starts_at must be an ISO 8601 datetime.')
    exam = Exam.objects.create(course=course, title=data['title'], starts_at=starts_at, venue=data['venue'], duration_minutes=data.get('duration_minutes', 120), instructions=data.get('instructions', ''), status=data.get('status', Exam.Status.DRAFT), created_by=request.user)
    return JsonResponse({'exam': exam_data(exam)}, status=201)


@authenticated
@require_http_methods(['GET', 'POST'])
def results(request):
    role = profile_data(request.user)['role']
    if request.method == 'GET':
        query = Result.objects.select_related('exam__course', 'student')
        if role == Profile.Role.STUDENT:
            query = query.filter(student=request.user, published=True)
        elif role == Profile.Role.LECTURER:
            query = query.filter(Q(exam__course__lecturer=request.user) | Q(exam__created_by=request.user)).distinct()
        return JsonResponse({'results': [result_data(item) for item in query]})
    if role not in (Profile.Role.LECTURER, Profile.Role.ADMIN):
        return error('Only lecturers and administrators can grade results.', 403)
    data = payload(request)
    if data is None or not data.get('exam_id') or not data.get('student_id'):
        return error('exam_id and student_id are required.')
    try:
        exam = Exam.objects.select_related('course').get(pk=data['exam_id'])
        student = User.objects.get(pk=data['student_id'])
    except (Exam.DoesNotExist, User.DoesNotExist):
        return error('Exam or student not found.', 404)
    if role == Profile.Role.LECTURER and exam.course.lecturer_id != request.user.id and exam.created_by_id != request.user.id:
        return error('You can only grade your own exams.', 403)
    if not hasattr(student, 'profile') or student.profile.role != Profile.Role.STUDENT:
        return error('Results can only be assigned to student accounts.')
    if not Enrollment.objects.filter(student=student, course=exam.course).exists():
        return error('The student is not enrolled in this exam course.', 400)
    result, _ = Result.objects.get_or_create(exam=exam, student=student)
    for field in ('internal_marks', 'exam_marks', 'total_marks', 'grade', 'semester', 'published'):
        if field in data:
            setattr(result, field, data[field])
    result.save()
    return JsonResponse({'result': result_data(result)})


@authenticated
@require_http_methods(['GET'])
def notifications(request):
    return JsonResponse({'notifications': [{'id': n.id, 'title': n.title, 'message': n.message, 'is_read': n.is_read, 'created_at': n.created_at.isoformat()} for n in request.user.notifications.all()]})


@authenticated
@csrf_exempt
@require_http_methods(['POST'])
def mark_notification_read(request, notification_id):
    updated = request.user.notifications.filter(pk=notification_id).update(is_read=True)
    if not updated:
        return error('Notification not found.', 404)
    return JsonResponse({'detail': 'Notification marked as read.'})


def frontend_file(request, file_path=''):
    """Development-only frontend host for the project's static HTML screens."""
    requested = file_path or 'home.html'
    root = settings.FRONTEND_DIR.resolve()
    target = (root / requested).resolve()
    try:
        target.relative_to(root)
    except ValueError as exc:
        raise Http404('File not found.') from exc
    if not target.is_file():
        raise Http404('File not found.')
    content_type, _ = mimetypes.guess_type(target.name)
    return FileResponse(target.open('rb'), content_type=content_type or 'application/octet-stream')
