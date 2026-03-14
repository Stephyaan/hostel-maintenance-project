# Dockerized Hostel Maintenance & Utility Management System

This project is fully containerized for development and production-ready deployments.

## Prerequisites
- Docker
- Docker Compose

## Quick Start
To launch the entire ecosystem (Backend + Frontend + Database):

```bash
docker compose up --build
```

## Services
- **Backend (Django)**: Accessible on `http://localhost:8000/api/`
- **Frontend (Nginx)**: Accessible on `http://localhost:8081/`

## Key Features of this Docker Setup
- **Security**: Backend runs as a non-root `appuser`.
- **Optimization**: Multi-stage style layering and `.dockerignore` files minimize image size.
- **Reliability**: Healthchecks ensure the frontend only routes traffic once the backend is live.
- **Independence**: Isolated networking for service communication.

## Management Commands
To run migrations inside Docker:
```bash
docker compose exec backend python manage.py migrate
```

To create a superuser:
```bash
docker compose exec backend python manage.py createsuperuser
```
