# Manipal Examination Management API

## Run locally

```powershell
cd backend
python manage.py migrate
python manage.py runserver
```

The API root is `http://127.0.0.1:8000/api/`. Obtain a JWT at `POST /api/token/`, then pass `Authorization: Bearer <access-token>`.
