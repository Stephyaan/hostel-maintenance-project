# Backend Implementation Plan: Hostel Maintenance System (Python/Django + SQLite)

This document outlines the roadmap for migrating the frontend-only prototype to a full-stack application using Django and SQLite.

## 1. Architecture Overview

-   **Frontend**: Existing HTML/CSS/JS files (currently in `frontend/`).
-   **Backend**: Django Framework (Python) serving REST APIs.
-   **Database**: SQLite (built-in with Django, ideal for this scale).
-   **Communication**: Frontend communicates with Backend via JSON APIs using `fetch()`.

---

## 2. Directory Structure

We will create a `backend` directory alongside the existing `frontend` directory.

```text
hostel_maintenance_project/
├── frontend/                 # Existing frontend files
│   ├── admin/
│   ├── student/
│   ├── supervisor/
│   └── static/
│
└── backend/                  # NEW Django Project
    ├── manage.py
    ├── hostel_backend/       # Project Settings
    │   ├── settings.py
    │   └── urls.py
    │
    └── api/                  # Main Application logic
        ├── models.py         # Database Schemas (Classes)
        ├── views.py          # API Logic (Functions)
        ├── serializers.py    # Data conversion (JSON <-> Python)
        └── urls.py           # API Endpoints
```

---

## 3. Database Schema (Models)

We will define these models in `api/models.py`.

### A. Users (Custom Model)
*   **Role**: Admin, Supervisor, Student, Worker
*   **Username/Email**
*   **Password** (Hashed)
*   **Room/Block** (For students)

### B. Complaints
*   **Title**
*   **Description**
*   **Room/Location**
*   **Priority**: Low, Medium, High
*   **Status**: Pending, Verified, In Progress, Resolved
*   **Created By** (ForeignKey to User)
*   **Assigned To** (ForeignKey to Worker, optional)
*   **Feedback**: Rating (1-5), Comment

### C. Resource Requests
*   **Item Name**
*   **Requested By** (Student)
*   **Status**: Pending, Approved, Rejected

### D. Notices
*   **Title**
*   **Content**
*   **Posted Date**
*   **Is Active**: Boolean

### E. Workers
*   **Name**
*   **Skill**: Plumbing, Electrical, etc.
*   **Phone**
*   **Status**: Available, Busy

---

## 4. Implementation Steps

### Phase 1: Setup & Configuration
1.  Check Python installation.
2.  Create virtual environment (`venv`).
3.  Install dependencies: `django`, `djangorestframework`, `django-cors-headers`.
4.  Initialize Django project (`hostel_backend`) and app (`api`).

### Phase 2: Database & Models
1.  Define models in `models.py`.
2.  Run migrations to create SQLite database tables.
3.  Register models in `admin.py` to view them in Django Admin Panel.

### Phase 3: API Development (DRF)
1.  Create **Serializers** to convert Model data to JSON.
2.  Create **Views** (API Endpoints) for:
    *   Auth (Login/Logout)
    *   Complaints (List, Create, Update, Delete)
    *   Notices (List, Create)
    *   Workers (List, Update)
3.  Configure URLs in `urls.py`.

### Phase 4: Frontend Integration
1.  Update `settings.py` to allow **CORS** (Cross-Origin Resource Sharing) so the frontend can call the backend.
2.  Refactor frontend JavaScript:
    *   Replace `localStorage.getItem()` with `fetch('http://localhost:8000/api/...')`.
    *   Replace `localStorage.setItem()` with `POST/PUT` requests.

---

## 5. Prerequisities

Before we begin, opens a terminal and verify Python:
`python --version`
