# Hostel Maintenance and Utility Management System

A comprehensive ecosystem for managing hostel maintenance requests, operational tracking, and utility management.

## 🚀 Features
- **Student Portal**: Lodge complaints and request resources.
- **Supervisor Portal**: Manage workers, track task lifecycles, and view efficiency metrics.
- **Admin Portal**: Global configuration, system-wide analytics, and user oversight.
- **Dockerized Architecture**: Simplified deployment using Docker and Nginx.

## 🛠️ Technology Stack
- **Backend**: Django & Django REST Framework
- **Frontend**: Vanilla HTML/JS with a minimalist "Plane" design
- **Database**: SQLite (Development) / PostgreSQL (Production ready)
- **Proxy**: Nginx for unified API access

## 🐳 Running with Docker
Ensure you have Docker and Docker Compose installed, then run:
```bash
docker-compose up --build
```
- **Frontend**: [http://localhost:8081/](http://localhost:8081/)
- **API**: [http://localhost:8081/api/](http://localhost:8081/api/)

## 📄 License
This project is licensed under the MIT License.
