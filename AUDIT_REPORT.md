# FamilyCare Project Audit Report

**Date**: 2026-10-15  
**Auditor**: Senior Full-Stack Engineer, QA Automation Engineer & Security Auditor  
**Application**: FamilyCare – Digital Family Health Record App  
**Environment**: Windows 11, Python 3.14.7, Flask 3.1.3, SQLite 3  

---

## 1. Project Architecture Discovered

FamilyCare is designed as a layered, full-stack digital health record and family health management web application.

```
┌─────────────────────────────────────────────────────────────────┐
│                          Web Browser                            │
│  (HTML5, CSS3 Custom Properties, Vanilla ES6 JavaScript,       │
│   Chart.js 4.4, Lucide Icons)                                   │
└──────────────────────────────┬──────────────────────────────────┘
                               │ HTTP / JSON REST APIs / Cookies
┌──────────────────────────────▼──────────────────────────────────┐
│                      Flask Application Layer                    │
│  - app.py: App Factory, Blueprint Registrations, Error Handlers │
│  - routes/: Pages & 19 API Blueprints                           │
│  - services/: Business logic (Auth, File, Search, Export, etc.) │
│  - utils/: Validators, Decorators, Constants, Helpers           │
└──────────────────────────────┬──────────────────────────────────┘
                               │ Parameterized SQL / SQLite WAL
┌──────────────────────────────▼──────────────────────────────────┐
│                       Data & Storage Layer                      │
│  - database/familycare.db (SQLite with Foreign Keys enabled)     │
│  - uploads/<user_id>/ (Sanitized, isolated document storage)    │
└─────────────────────────────────────────────────────────────────┘
```

### Technology Breakdown
- **Frontend**: Responsive multi-page web architecture using Jinja2 templates (`templates/`), responsive CSS with CSS variables (`static/css/style.css`), and modular client-side JavaScript (`static/js/api.js`, `static/js/app.js`, `static/js/*.js`). Chart visualizations powered by Chart.js; iconography powered by Lucide.
- **Backend**: Python 3.14 with Flask 3.1.3, Flask-Login 0.6.3 for session-based user authentication, Flask-WTF for CSRF protection, and Werkzeug for password hashing (`pbkdf2:sha256`) and secure filename handling.
- **Database**: SQLite 3 database (`database/familycare.db`) configured with `PRAGMA foreign_keys = ON` and `PRAGMA journal_mode = WAL`. 15 relational tables with cascading foreign keys to `users` and `family_members`.
- **File Storage**: Local filesystem storage segregated per user (`uploads/<user_id>/<stored_filename>`) with randomized unique filenames, MIME extension validation, 10MB size limits, and access control verifying user ownership before download.

---

## 2. Backend & Database Findings

### Launch Path Independence
- **Issue**: `config.py` previously initialized relative paths (`database/familycare.db` and `uploads`), causing the application to create empty databases or fail file uploads if executed from outside the project root directory.
- **Resolution**: `config.py` was updated to resolve paths using `BASE_DIR = os.path.abspath(os.path.dirname(__file__))`, guaranteeing absolute path resolution. A safe backup of the database was archived to `database/familycare.db.bak`.

### Relational Schema & Integrity
- All tables feature primary keys (`id INTEGER PRIMARY KEY AUTOINCREMENT`) and foreign keys to `users(id)` and `family_members(id)`.
- Foreign key constraints are enforced on every database connection via `PRAGMA foreign_keys = ON` in `models/db.py`.
- Deleting an account initiates cascade deletion across all personal records, documents, expenses, and policies.
- Archival support (`is_archived = 1`) was integrated into `models/family_member.py` and exposed via `/api/family-members/<id>/archive` to safely archive family member profiles without cascading deletion of their underlying medical history.

---

## 3. Feature Inventory

| Module | Route / Page | API Endpoint | Database Table | Status |
|---|---|---|---|---|
| **Landing Page** | `/` | N/A | N/A | Fully Functional |
| **Authentication** | `/login`, `/register` | `/api/auth/*` | `users` | Fully Functional |
| **User Profile & Settings** | `/settings` | `/api/users/*` | `users` | Fully Functional |
| **Main Dashboard** | `/dashboard` | `/api/dashboard/*` | Aggregated | Fully Functional |
| **Family Member Management** | `/family` | `/api/family-members/*` | `family_members` | Fully Functional |
| **Member Health Profile** | `/member/<id>` | `/api/family-members/<id>/summary` | Aggregated | Fully Functional |
| **Medical Records** | `/records` | `/api/records/*` | `medical_records` | Fully Functional |
| **Document Upload & Storage**| N/A | `/api/documents/*` | `medical_documents` | Fully Functional |
| **Prescriptions** | In Records/Member | `/api/prescriptions/*` | `prescriptions` | Fully Functional |
| **Medicines Tracking** | `/medicines` | `/api/medicines/*` | `medicines` | Fully Functional |
| **Medicine Reminders** | `/reminders` | `/api/reminders/*` | `medicine_reminders` | Fully Functional |
| **Doctor Visits / Appointments**| `/appointments` | `/api/appointments/*` | `doctor_visits` | Fully Functional |
| **Tests & Follow-ups** | `/tests` | `/api/tests/*` | `tests` | Fully Functional |
| **Vaccinations** | `/vaccinations` | `/api/vaccinations/*` | `vaccinations` | Fully Functional |
| **Health Parameter Tracker** | `/health-tracker` | `/api/health-parameters/*` | `health_parameters` | Fully Functional |
| **Health Timeline** | `/timeline` | `/api/timeline` | Multi-table UNION | Fully Functional |
| **Medical Expense Tracker** | `/expenses` | `/api/expenses/*` | `expenses` | Fully Functional |
| **Insurance Policies & Claims**| `/insurance` | `/api/insurance/*` | `insurance_policies`, `claims` | Fully Functional |
| **Emergency Information** | `/emergency` | `/api/emergency/*` | `family_members` | Fully Functional |
| **Notifications** | `/notifications` | `/api/notifications/*` | `notifications` | Fully Functional |
| **Export & Backup** | `/settings` | `/api/export/*` | All medical tables | Fully Functional |
| **Global Search** | `/search` | `/api/search` | Multi-table Search | Fully Functional |
| **Admin Module** | `/admin` | `/api/admin/*` | `users`, `audit_logs` | Fully Functional |
| **Dark Mode / Light Mode** | Persistent Header Toggle | Client `localStorage` | N/A | Fully Functional |

---

## 4. Key Bugs Found & Fixes Applied

1. **Document Upload/Download Crash (`routes/documents.py`)**:
   - *Cause*: `save_file(file, 'documents')` was called with 2 arguments instead of 5 (`file, category, user_id, family_member_id, record_id`), raising a Python `TypeError`. Downloads called `get_file_path(doc['file_path'])` instead of passing `(doc_id, user_id)`.
   - *Fix*: Refactored `routes/documents.py` to forward `current_user.id` and form metadata properly to `file_service.py`, verifying file existence on disk before calling `send_file`.
2. **Export Functionality Failures (`routes/export.py` & `services/export_service.py`)**:
   - *Cause*: `export_backup_json` and `export_csv` returned raw strings, but `routes/export.py` passed these strings directly into Flask's `send_file()`, crashing with `FileNotFoundError` / `ValueError`. Furthermore, `export_family_summary` queried non-existent columns `parameter_value` and `measured_at` in `health_parameters`.
   - *Fix*: Wrapped export strings in `io.BytesIO(str.encode('utf-8'))` with explicit mimetypes and attachment headers. Corrected `health_parameters` column names to `value, record_date, record_time`.
3. **Weak Password Registration Vulnerability (`services/auth_service.py`)**:
   - *Cause*: `register_user` was not executing `validate_password` or `validate_email`, permitting 3-character passwords.
   - *Fix*: Integrated `utils/validators.py` into `services/auth_service.py` to enforce minimum 8 characters, mixed case, numbers, and special symbols.
4. **Global Search Hospital & Member Name Blindspot (`services/search_service.py`)**:
   - *Cause*: Queries for medical records, appointments, and tests omitted `r.hospital` and `fm.name` from their search filters, causing queries for hospital names or patient names to return empty lists.
   - *Fix*: Added parameterized searches for `hospital`, `specialization`, and `fm.name` across all 5 searched categories.
5. **Health Parameter Aliasing Defect (`models/health_parameter.py`)**:
   - *Cause*: Payload field `parameter_value` was not mapped to database column `value`, triggering SQLite `NOT NULL constraint failed: health_parameters.value`.
   - *Fix*: Added automatic aliasing in `HealthParameter.create()` from `parameter_value` / `reading` to `value`.
6. **Admin Panel DOM & Route Disconnect (`routes/admin.py` & `static/js/admin.js`)**:
   - *Cause*: Routes returned mock stub data; frontend JS queried obsolete element IDs (`#total-users`, `#users-table tbody`) that threw uncaught `TypeError`s.
   - *Fix*: Re-implemented `routes/admin.py` with live SQL aggregations and user status management. Rewrote `static/js/admin.js` targeting actual DOM IDs with tab switching and search.

---

## 5. Security Findings & Posture

- **Password Storage**: Passwords are never stored in plaintext. They are salted and hashed using PBKDF2-HMAC-SHA256 (`generate_password_hash`).
- **Data Isolation**: All database queries strictly scope rows by `WHERE user_id = current_user.id`. Tests confirmed that User B cannot read, update, delete, or export User A's members, records, or documents.
- **SQL Injection**: Parameterized SQL queries (`?` placeholders) are used throughout all models. Negative testing with `' OR '1'='1` confirmed zero injection vulnerability.
- **XSS Sanitization**: User inputs are escaped by Jinja2 templates by default, and `App.utils.escapeHtml` is used across all client-side JavaScript renderers.
- **File Upload Security**: Uploaded documents are renamed using UUIDs, extensions are strictly validated (`.pdf`, `.jpg`, `.jpeg`, `.png`), stored outside public static folders, and served only through an authenticated endpoint enforcing ownership.

---

## 6. Known Limitations & External Dependencies

- **Client-Side Notifications**: Medicine reminders currently trigger browser toast notifications when the user is logged into the application. There is no external SMS/WhatsApp/Push gateway configured, which is standard for a local B.Tech CSE deployment.
- **Chart.js CDN & Lucide Icons**: Loaded via CDN (`cdnjs.cloudflare.com` / `unpkg.com`). Offline operation requires caching these static assets locally if deployed without an internet connection.
- **Database Scalability**: Powered by SQLite in WAL mode. For production high-concurrency environments, migrating the SQLite schema to PostgreSQL or MySQL can be accomplished with standard relational DDL.
