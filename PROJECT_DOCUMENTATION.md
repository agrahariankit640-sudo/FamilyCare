# FamilyCare – Project Documentation
## Digital Family Health Record Management System

### 1. Objective
To design and develop a web-based application that allows users to digitally manage, track, and organize the health records of their entire family in a secure and intuitive platform.

### 2. Problem Statement
Managing health records for multiple family members involves dealing with scattered paper prescriptions, hard-to-find lab reports, and forgotten medical history. In emergencies, the lack of immediate access to consolidated medical data can be critical. There is a need for a unified digital platform to track health metrics, appointments, and records efficiently.

### 3. Proposed Solution
FamilyCare provides a centralized digital platform where users can create profiles for each family member, upload medical documents, log health parameters (like blood pressure or sugar levels), track medication schedules, and manage medical expenses. The system features an intuitive dashboard that gives a quick overview of upcoming appointments and recent health metrics.

### 4. Methodology
Agile development methodology was adopted for this project, allowing iterative progress, continuous testing, and the flexibility to adapt to changing requirements. The development involved sequential sprints focusing on specific modules (e.g., Auth, Profile Management, Records Management).

### 5. System Architecture
```
+----------------+      +----------------+      +-------------------+
|                |      |                |      |                   |
|  Web Browser   +----->+   Flask App    +----->+  SQLite Database  |
|  (Client)      |      |   (Backend)    |      |  (Data Storage)   |
|                |      |                |      |                   |
+----------------+      +----------------+      +-------------------+
        ^                       |
        |                       v
        +-----------------------+
           HTML/CSS/JS Views
```

### 6. Module Descriptions
1. **Authentication Module**: Handles user registration, login, logout, and session management securely.
2. **Family Member Module**: Allows creation, updating, and deletion of family member profiles containing basic health info like blood group and allergies.
3. **Medical Records Module**: Facilitates uploading and categorizing lab reports, prescriptions, and imaging files.
4. **Medicines & Reminders Module**: Tracks active prescriptions and sets up schedules/reminders.
5. **Appointments Module**: Logs upcoming and past doctor visits.
6. **Analytics Module**: Visualizes health parameters over time using Chart.js.
7. **Expenses Module**: Tracks medical expenditures for budgeting.
8. **Insurance Module**: Manages health insurance policy details and renewal dates.

### 7. Database Design
The relational database is designed with normalized tables to ensure data integrity. 
- `users` (1) : (M) `members`
- `members` (1) : (M) `records`
- `members` (1) : (M) `health_parameters`
- `members` (1) : (M) `medicines`
- `medicines` (1) : (M) `reminders`
(ER Diagram Description: A central `users` table linked to multiple `members`, which in turn branch out to their respective `records`, `medicines`, and `tests`.)

### 8. Functional Requirements
- Users shall be able to register and log in securely.
- Users shall be able to add multiple family members.
- Users shall be able to upload files for medical records.
- The system shall display a dashboard summarizing upcoming appointments.
- The system shall prevent a user from accessing another user's family data.
- The system shall allow tracking of customized health parameters.

### 9. Non-Functional Requirements
- **Performance**: The system should respond to typical user actions in under 1 second.
- **Security**: Passwords must be hashed. CSRF protection must be enabled.
- **Usability**: The interface must be responsive and accessible on mobile devices.
- **Reliability**: The system should maintain data integrity during concurrent accesses.

### 10. Technology Stack
- **Frontend**: HTML5, CSS3, Vanilla JavaScript, Chart.js for data visualization.
- **Backend**: Python 3, Flask framework.
- **Database**: SQLite.
- **Tools**: pytest for unit testing, Git for version control.

### 11. Screenshots
- *Login Page*: Clean, centered login form.
- *Dashboard*: Summary cards and health trends charts.
- *Member Profile*: Detailed view of a family member's records and history.
- *Add Record Modal*: Form for uploading files and inputting metadata.

### 12. Testing
Testing was conducted using pytest, focusing on:
- Unit tests for all utility functions.
- Integration tests for API endpoints and database operations.
- Security tests validating data ownership constraints.
Results: All tests passing with adequate coverage on critical authentication and ownership modules.

### 13. Future Scope
- Integration with wearable devices for automated health parameter logging.
- AI-based symptom checker and trend analysis.
- Telemedicine integration for online consultations.
- Multi-language support for better accessibility.

### 14. Conclusion
The FamilyCare project successfully demonstrates a functional, secure, and user-friendly digital health record management system. It solves the critical problem of fragmented medical data by providing a consolidated platform for families.

### 15. References
- Flask Documentation: https://flask.palletsprojects.com/
- Chart.js Documentation: https://www.chartjs.org/
- SQLite Documentation: https://www.sqlite.org/
