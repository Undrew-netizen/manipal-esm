# Manipal EMS backend

The backend is a Django application using SQLite and Django session authentication. It also serves the existing `frontend/` folder in development, so the HTML pages and `/api/` calls run from the same origin.

## Run locally

From `backend/` on Windows:

```powershell
.\manipal\Scripts\python.exe manage.py migrate
.\manipal\Scripts\python.exe runserver
```

Open `http://127.0.0.1:8000/login.html`.

## API

- `POST /api/auth/register/` — student account creation
- `POST /api/auth/login/` and `POST /api/auth/logout/`
- `GET`/`PATCH /api/me/` — current profile
- `GET /api/dashboard/` — role-aware dashboard data
- `GET`/`POST /api/exams/` — exams; creation is restricted to lecturers/admins
- `GET`/`POST /api/results/` — results; grading is restricted to lecturers/admins
- `GET /api/notifications/`
- `POST /api/notifications/{id}/read/`

Use the Django admin at `/admin/` to create lecturer/admin users, courses, enrollments, and notifications. Create an administrator with `manage.py createsuperuser`, then set that user's profile role to `admin` in the Django admin.
