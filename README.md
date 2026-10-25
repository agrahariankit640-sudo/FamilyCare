# FamilyCare – Digital Family Health Record App

> Your Family's Health, Organized in One Place.

## Overview
FamilyCare is a comprehensive digital family health record management platform designed to help users track and manage the health information of their entire family in one secure, centralized location.

## Features
1. User Authentication (Register/Login)
2. Family Member Profile Management
3. Medical Records Storage (Lab reports, Prescriptions)
4. Medicine Tracking and Reminders
5. Doctor Appointment Scheduling and Logging
6. Medical Test Tracking
7. Vaccination Schedules
8. Health Parameters Monitoring (BP, Sugar, Weight, etc.)
9. Medical Expense Tracking
10. Health Insurance Policy Management
11. Notifications and Alerts
12. Dashboard Summaries and Analytics
13. Search and Filter functionality
14. Data Export capabilities
15. Role-based Access Control
16. Secure File Uploads
17. Audit Logging
18. Responsive Web Design
19. Interactive Charts
20. Profile Customization

## Technology Stack
- Frontend: HTML5, CSS3, Vanilla JavaScript, Chart.js
- Backend: Python 3.x, Flask
- Database: SQLite
- Authentication: Flask-Login with server-side sessions
- Security: CSRF protection, password hashing, input validation

## Architecture
The application follows a standard monolithic web application architecture. It uses the MVC (Model-View-Controller) pattern adapted for Flask (Models/Views/Templates). The frontend communicates with the backend via standard HTTP requests and form submissions, as well as some AJAX for dynamic interactions.

## Project Structure
```
FamilyCare/
├── app.py
├── config.py
├── seed.py
├── requirements.txt
├── README.md
├── PROJECT_DOCUMENTATION.md
├── .env.example
├── models/
│   ├── __init__.py
│   ├── db.py
│   └── models.py
├── routes/
│   ├── __init__.py
│   ├── auth.py
│   ├── dashboard.py
│   ├── family.py
│   └── records.py
├── static/
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   └── main.js
│   └── uploads/
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   └── dashboard/
└── tests/
    ├── __init__.py
    ├── conftest.py
    └── test_*.py
```

## Database Schema
1. `users` (id, name, email, password_hash, role)
2. `members` (id, user_id, name, relationship, gender, dob, blood_group, allergies, chronic_conditions)
3. `records` (id, member_id, title, description, date, record_type, file_path)
4. `medicines` (id, member_id, name, dosage, frequency, status)
5. `reminders` (id, medicine_id, reminder_date, time, status)
6. `doctor_visits` (id, member_id, doctor_name, specialty, visit_date, status)
7. `tests` (id, member_id, test_name, test_date, result, follow_up_date)
8. `vaccinations` (id, member_id, vaccine_name, administered_date, dose_details, next_due_date)
9. `health_parameters` (id, member_id, parameter_name, value, reading_date)
10. `expenses` (id, user_id, member_id, description, amount, date, category)
11. `insurance_policies` (id, user_id, provider_name, policy_number, holder_name, member_id, start_date, expiry_date, coverage_amount, premium_amount)
12. `notifications` (id, user_id, message, status, created_at)
13. `audit_logs` (id, user_id, action, details)
(other supporting tables)

## Installation
1. Clone the repository
2. Create virtual environment: `python -m venv venv`
3. Activate: `venv\Scripts\activate` (Windows) or `source venv/bin/activate` (Linux/Mac)
4. Install dependencies: `pip install -r requirements.txt`
5. Copy .env.example to .env and update SECRET_KEY
6. Run the application: `python app.py`
7. (Optional) Seed demo data: `python seed.py`
8. Open http://localhost:5000

## Default Accounts
| Role | Email | Password |
|------|-------|----------|
| Admin | admin@familycare.com | Admin@123 |
| Demo User | demo@familycare.com | Demo@123 |

## API Overview
- `/auth/*`: Authentication routes (login, register, logout)
- `/dashboard/*`: Dashboard view routes
- `/family/*`: Member management CRUD
- `/records/*`: Medical records CRUD
- `/medicines/*`: Medicines and reminders
- `/appointments/*`: Doctor visits

## Running Tests
```
python -m pytest tests/ -v
```

## Security Notes
- Passwords hashed using werkzeug.security
- Session management via Flask-Login
- Input sanitization and validation on all forms
- Protected routes requiring authentication
- Data ownership checks (users can only access their own family's data)
- Secure file upload handling

## Known Limitations
- SQLite database is not suitable for high concurrency deployments
- File storage is local to the server
- Email notifications are simulated

## Future Scope
- Integration with cloud storage (AWS S3) for medical records
- Machine learning for health parameter trend predictions
- Mobile application using React Native
- Direct integration with pathology labs for automated report fetching

## License
This project is developed for educational purposes.

## Disclaimer
This application is a health record management tool, not a medical diagnosis system. Always consult a qualified healthcare provider for medical advice.
