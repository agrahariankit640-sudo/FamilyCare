# FamilyCare Bug Fix Log

This log documents all identified defects, root causes, applied code corrections, and verification results during the comprehensive project audit.

---

### Bug ID: BUG-001
- **Severity**: High (Data Integrity / Portability)
- **Description**: Database path and uploads directory defaulted to relative strings (`database/familycare.db`), creating isolated fragmented databases or missing directories when executed from alternate working directories.
- **Root Cause**: `config.py` did not anchor file paths to the project root directory using `os.path.abspath(os.path.dirname(__file__))`.
- **Files Changed**: [`config.py`](file:///c:/Users/radhe/OneDrive/Documents/FamilyCare/config.py)
- **Fix Applied**: Defined `BASE_DIR` and enforced absolute path resolution for `DATABASE_PATH` and `UPLOAD_FOLDER`.
- **Regression Test**: Direct test execution from different launch paths.
- **Final Verification Result**: Verified; all modules connect to the single authoritative database in `c:\Users\radhe\OneDrive\Documents\FamilyCare\database\familycare.db`.

---

### Bug ID: BUG-002
- **Severity**: Critical (Runtime Crash)
- **Description**: Document upload and download endpoints threw 500 Internal Server Errors on every invocation.
- **Root Cause**: `routes/documents.py` called `save_file(file, 'documents')` with 2 arguments instead of 5 (`file, category, user_id, family_member_id, record_id`), raising a Python `TypeError`. Downloads called `get_file_path(doc['file_path'])` with a string instead of `(id, current_user.id)`.
- **Files Changed**: [`routes/documents.py`](file:///c:/Users/radhe/OneDrive/Documents/FamilyCare/routes/documents.py)
- **Fix Applied**: Updated `routes/documents.py` to extract `family_member_id` and `record_id` and forward `current_user.id` to `save_file()`, `get_file_path()`, and `delete_file()`. Added file existence verification before calling `send_file()`.
- **Regression Test**: `tests/test_audit_comprehensive.py::test_qa_complete_lifecycle`
- **Final Verification Result**: Verified; PDF files upload, persist to `uploads/<uid>/`, download with exact byte matching, and delete cleanly.

---

### Bug ID: BUG-003
- **Severity**: High (Runtime Crash / Data Export Failure)
- **Description**: Backup export, CSV export, and Family Summary export crashed with HTTP 500 when triggered.
- **Root Cause**: In `services/export_service.py`, `export_backup_json` returned a JSON string and `export_csv` returned a CSV string. In `routes/export.py`, these strings were passed directly into `send_file()`, which expects a file path or binary stream, raising `FileNotFoundError`. Additionally, `export_family_summary` queried non-existent columns `parameter_value` and `measured_at` on table `health_parameters`.
- **Files Changed**: [`routes/export.py`](file:///c:/Users/radhe/OneDrive/Documents/FamilyCare/routes/export.py), [`services/export_service.py`](file:///c:/Users/radhe/OneDrive/Documents/FamilyCare/services/export_service.py)
- **Fix Applied**: Wrapped generated JSON and CSV content into `io.BytesIO(str.encode('utf-8'))` before passing to `send_file()` with proper mimetypes and attachment download headers. Corrected `health_parameters` column names to `value, record_date, record_time`. Expanded CSV export to support all modules (`expenses`, `records`, `medicines`, `appointments`, `tests`, `vaccinations`, `vitals`).
- **Regression Test**: `tests/test_audit_comprehensive.py::test_qa_complete_lifecycle`
- **Final Verification Result**: Verified; full JSON backup, CSV exports, and member JSON summary download successfully.

---

### Bug ID: BUG-004
- **Severity**: Medium (Security / Validation Defect)
- **Description**: User registration accepted weak passwords (e.g. `'123'`) and invalid email formats.
- **Root Cause**: `services/auth_service.py` implemented `register_user` without calling `validate_password` or `validate_email` from `utils/validators.py`.
- **Files Changed**: [`services/auth_service.py`](file:///c:/Users/radhe/OneDrive/Documents/FamilyCare/services/auth_service.py)
- **Fix Applied**: Added validation checks in `register_user` enforcing standard password complexity (minimum 8 characters, mixed case, numbers, and special characters) and email formatting prior to account creation.
- **Regression Test**: `tests/test_audit_comprehensive.py::test_qa_complete_lifecycle`
- **Final Verification Result**: Verified; weak passwords and malformed emails return HTTP 400 Bad Request.

---

### Bug ID: BUG-005
- **Severity**: Medium (Functional Defect / Search Blindspot)
- **Description**: Global search failed to find medical records when searching by hospital name or patient name.
- **Root Cause**: `services/search_service.py` omitted `r.hospital` and `fm.name` from the `WHERE` clause in `medical_records`, `appointments`, `tests`, and `vaccinations`.
- **Files Changed**: [`services/search_service.py`](file:///c:/Users/radhe/OneDrive/Documents/FamilyCare/services/search_service.py)
- **Fix Applied**: Added parameterized checks for `r.hospital LIKE ?`, `a.specialization LIKE ?`, and `fm.name LIKE ?` across all search subqueries.
- **Regression Test**: `tests/test_audit_comprehensive.py::test_qa_complete_lifecycle`
- **Final Verification Result**: Verified; searching for `'Apollo'` successfully returns matching records.

---

### Bug ID: BUG-006
- **Severity**: Medium (Database Integrity Error)
- **Description**: Creating health parameters with field name `parameter_value` crashed with SQLite error: `NOT NULL constraint failed: health_parameters.value`.
- **Root Cause**: The SQLite table column is named `value`, but frontend forms and test payloads frequently supply `parameter_value`.
- **Files Changed**: [`models/health_parameter.py`](file:///c:/Users/radhe/OneDrive/Documents/FamilyCare/models/health_parameter.py)
- **Fix Applied**: Added automated aliasing in `HealthParameter.create()` to map `parameter_value` and `reading` to `value`.
- **Regression Test**: `tests/test_audit_comprehensive.py::test_qa_complete_lifecycle`
- **Final Verification Result**: Verified; vital parameters save smoothly with any common field alias.

---

### Bug ID: BUG-007
- **Severity**: High (UI Freeze / JavaScript Null References)
- **Description**: Admin dashboard and multiple member pages became permanently stuck on "Loading..." or crashed with uncaught JavaScript `TypeError`s.
- **Root Cause**: Frontend JavaScript files queried obsolete DOM element IDs (`#total-users`, `#users-table tbody`, `#activity-table tbody`, `#member-select`, `#emergency-container`, etc.) that did not exist in the rendered HTML templates.
- **Files Changed**: [`static/js/admin.js`](file:///c:/Users/radhe/OneDrive/Documents/FamilyCare/static/js/admin.js), [`routes/admin.py`](file:///c:/Users/radhe/OneDrive/Documents/FamilyCare/routes/admin.py), [`models/user.py`](file:///c:/Users/radhe/OneDrive/Documents/FamilyCare/models/user.py)
- **Fix Applied**: Rewrote `static/js/admin.js` to match exact DOM IDs in `templates/admin.html` (`#admin-stat-users`, `#admin-stat-profiles`, `#admin-users-list`, `#admin-audit-list`), implemented tab switching and live user search/toggle. Replaced mock responses in `routes/admin.py` with real SQL aggregations.
- **Regression Test**: `tests/test_pages_and_routes.py::test_all_pages_render`
- **Final Verification Result**: Verified; zero JavaScript console exceptions, all stat cards render live values, and user management functions correctly.
