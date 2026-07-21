# Manipal EMS

This repository contains a Django backend and a static frontend for the Manipal EMS application.

## Prerequisites

- Python 3.11+ installed
- pip installed
- Git installed

## Setup

1. Clone the repository:

```bash
git clone https://github.com/Undrew-netizen/manipal-esm.git
cd "MANIPAL EMS"
```

2. Create and activate a Python virtual environment:

Windows:
```bash
python -m venv backend\venv
backend\venv\Scripts\activate
```

Mac/Linux:
```bash
python3 -m venv backend/venv
source backend/venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r backend/requirements.txt
```

4. Run database migrations:

```bash
cd backend
python manage.py migrate
```

5. Create a superuser (optional):

```bash
python manage.py createsuperuser
```

6. Run the development server:

```bash
python manage.py runserver
```

7. Open the frontend pages directly in your browser from `frontend/`, or serve them from a simple web server if needed.

## Docker setup

If you want the project to run from a fresh clone with everything contained in one environment, use Docker.

1. Build and run the app:

```bash
docker compose up --build
```

2. The Django backend will be available at:

```text
http://127.0.0.1:8000
```

3. To stop the app:

```bash
docker compose down
```

## Notes

- The backend uses `backend/db.sqlite3` by default. If you want that database to travel with the repo, keep it tracked in Git.
- `backend/media/` is mounted into the container so uploaded files can persist while the container runs.
- If you use a different port for the frontend or backend, update `docker-compose.yml` and `backend/manipal/settings.py`.
