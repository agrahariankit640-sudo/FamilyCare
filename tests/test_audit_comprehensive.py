import io
import json
import pytest
from models.user import User
from models.db import get_db

def test_qa_complete_lifecycle(app, client):
    # ---------------------------------------------------------
    # 1. Registration & Auth
    # ---------------------------------------------------------
    email = "qa.familycare@example.test"
    password = "TestPassword@2026"
    
    # Negative registration test: missing fields
    res_neg = client.post('/api/auth/register', json={'email': email})
    assert res_neg.status_code == 400
    
    # Negative registration test: weak password
    res_weak = client.post('/api/auth/register', json={
        'name': 'FamilyCare QA User',
        'email': 'weak@example.test',
        'password': '123'
    })
    assert res_weak.status_code == 400

    # Successful registration
    reg_res = client.post('/api/auth/register', json={
        'name': 'FamilyCare QA User',
        'email': email,
        'password': password,
        'phone': '+91 9988776655'
    })
    assert reg_res.status_code == 201 or reg_res.status_code == 200
    
    # Duplicate registration prevention
    dup_res = client.post('/api/auth/register', json={
        'name': 'FamilyCare QA User',
        'email': email,
        'password': password
    })
    assert dup_res.status_code == 409 or dup_res.status_code == 400

    # Verify password is not plaintext in DB
    with app.app_context():
        user_row = User.get_by_email(email)
        assert user_row is not None
        assert user_row['password_hash'] != password
        assert 'pbkdf2' in user_row['password_hash'] or 'scrypt' in user_row['password_hash']


    # Login with wrong password
    bad_login = client.post('/api/auth/login', json={'email': email, 'password': 'WrongPassword!'})
    assert bad_login.status_code == 401

    # Login with correct password
    login_res = client.post('/api/auth/login', json={'email': email, 'password': password})
    assert login_res.status_code == 200
    assert login_res.get_json()['success'] is True

    # Check /api/auth/me
    me_res = client.get('/api/auth/me')
    assert me_res.status_code == 200
    user_info = me_res.get_json()['data']
    assert user_info['email'] == email
    assert 'password_hash' not in user_info

    # ---------------------------------------------------------
    # 2. Family Members Creation & Archival
    # ---------------------------------------------------------
    # Member A: Aarav Sharma
    res_a = client.post('/api/family-members/', json={
        'name': 'Aarav Sharma',
        'relationship': 'Self',
        'gender': 'Male',
        'date_of_birth': '1998-04-12',
        'blood_group': 'O+',
        'phone': '+91 9988776655',
        'emergency_contact': 'Meera Sharma',
        'emergency_contact_phone': '+91 9876543210',
        'allergies': 'Dust, Pollen',
        'existing_conditions': 'Mild Asthma'
    })
    assert res_a.status_code == 200
    member_a_id = res_a.get_json()['data']['id']

    # Member B: Meera Sharma
    res_b = client.post('/api/family-members/', json={
        'name': 'Meera Sharma',
        'relationship': 'Mother',
        'gender': 'Female',
        'date_of_birth': '1975-08-22',
        'blood_group': 'B+',
        'phone': '+91 9876543210',
        'allergies': 'Penicillin',
        'existing_conditions': 'Hypertension'
    })
    assert res_b.status_code == 200
    member_b_id = res_b.get_json()['data']['id']

    # Member C: Kabir Sharma
    res_c = client.post('/api/family-members/', json={
        'name': 'Kabir Sharma',
        'relationship': 'Brother',
        'gender': 'Male',
        'date_of_birth': '2005-01-15',
        'blood_group': 'A+'
    })
    assert res_c.status_code == 200
    member_c_id = res_c.get_json()['data']['id']

    # Verify all members returned
    list_res = client.get('/api/family-members/')
    assert list_res.status_code == 200
    members = list_res.get_json()['data']
    assert len(members) == 3

    # Update Member A
    update_res = client.put(f'/api/family-members/{member_a_id}', json={
        'allergies': 'Dust, Pollen, Peanuts'
    })
    assert update_res.status_code == 200

    # Archive Member C
    archive_res = client.put(f'/api/family-members/{member_c_id}/archive')
    assert archive_res.status_code == 200

    # Verify active list now has 2 members
    list_active = client.get('/api/family-members/').get_json()['data']
    assert len(list_active) == 2

    # ---------------------------------------------------------
    # 3. Medical Records & Document Upload
    # ---------------------------------------------------------
    rec_res = client.post('/api/records/', json={
        'family_member_id': member_a_id,
        'title': 'Annual Preventive Checkup',
        'record_type': 'Consultation',
        'record_date': '2026-05-10',
        'doctor': 'Dr. Ananya Roy',
        'hospital': 'Apollo Hospital',
        'diagnosis': 'Healthy, low Vitamin D',
        'notes': 'Start Vitamin D supplements and retest in 2 months'
    })
    assert rec_res.status_code == 200
    record_id = rec_res.get_json()['data']['id']

    # Document upload test: valid PDF
    pdf_bytes = b"%PDF-1.4 test synthetic medical report content"
    upload_res = client.post('/api/documents/upload', data={
        'document': (io.BytesIO(pdf_bytes), 'checkup_report.pdf'),
        'family_member_id': member_a_id,
        'record_id': record_id,
        'category': 'reports'
    }, content_type='multipart/form-data')
    assert upload_res.status_code == 200
    doc_id = upload_res.get_json()['data']['id']

    # Retrieve document
    doc_get = client.get(f'/api/documents/{doc_id}')
    assert doc_get.status_code == 200
    assert doc_get.data == pdf_bytes

    # Document upload test: invalid file type (.exe)
    bad_upload = client.post('/api/documents/upload', data={
        'document': (io.BytesIO(b'malicious content'), 'malware.exe'),
        'family_member_id': member_a_id
    }, content_type='multipart/form-data')
    assert bad_upload.status_code == 400

    # ---------------------------------------------------------
    # 4. Prescriptions & Medicines
    # ---------------------------------------------------------
    rx_res = client.post('/api/prescriptions/', json={
        'family_member_id': member_a_id,
        'medicine_name': 'Vitamin D3',
        'doctor': 'Dr. Ananya Roy',
        'prescription_date': '2026-05-10',
        'dosage': '60000 IU',
        'frequency': 'Weekly',
        'duration': '8 weeks',
        'instructions': 'Take after food on Sunday'
    })
    assert rx_res.status_code == 200
    rx_id = rx_res.get_json()['data']['id']

    med_res = client.post('/api/medicines/', json={
        'family_member_id': member_a_id,
        'name': 'Vitamin D3',
        'dosage': '60000 IU',
        'frequency': 'Weekly',
        'start_date': '2026-05-10',
        'end_date': '2026-07-05',
        'instructions': 'Weekly capsule after breakfast',
        'doctor_prescribed': 'Dr. Ananya Roy'
    })
    assert med_res.status_code == 200
    med_id = med_res.get_json()['data']['id']

    # Medicine reminders
    rem_res = client.post('/api/reminders/', json={
        'medicine_id': med_id,
        'reminder_time': '09:00',
        'days_of_week': 'Sun'
    })
    assert rem_res.status_code == 200
    rem_id = rem_res.get_json()['data']['id']

    # Update reminder status
    rem_update = client.put(f'/api/reminders/{rem_id}/status', json={'status': 'taken'})
    assert rem_update.status_code == 200

    # ---------------------------------------------------------
    # 5. Doctor Visits, Tests & Vaccinations
    # ---------------------------------------------------------
    appt_res = client.post('/api/appointments/', json={
        'family_member_id': member_a_id,
        'doctor_name': 'Dr. Rajiv Verma',
        'specialty': 'Cardiology',
        'hospital': 'Max Healthcare',
        'visit_date': '2026-11-20',
        'visit_time': '10:30',
        'reason': 'Routine Cardiac Checkup'
    })
    assert appt_res.status_code == 200

    test_res = client.post('/api/tests/', json={
        'family_member_id': member_a_id,
        'test_name': 'Serum 25-Hydroxy Vitamin D',
        'laboratory': 'Thyrocare Labs',
        'test_date': '2026-05-15',
        'result': '18 ng/mL (Low)',
        'followup_date': '2026-07-15'
    })
    assert test_res.status_code == 200

    vax_res = client.post('/api/vaccinations/', json={
        'family_member_id': member_a_id,
        'vaccine_name': 'Hepatitis B Booster',
        'date_administered': '2026-01-10',
        'dose_number': 3,
        'hospital_name': 'City Health Center',
        'next_due_date': '2031-01-10'
    })
    assert vax_res.status_code == 200

    # ---------------------------------------------------------
    # 6. Health Parameters & Trends
    # ---------------------------------------------------------
    bp_res = client.post('/api/health-parameters/', json={
        'family_member_id': member_a_id,
        'parameter_name': 'Blood Pressure',
        'parameter_value': '120/80',
        'unit': 'mmHg',
        'record_date': '2026-05-10',
        'record_time': '08:30'
    })
    assert bp_res.status_code == 200

    trends_res = client.get(f'/api/health-parameters/trends?member_id={member_a_id}&parameter=Blood Pressure')
    assert trends_res.status_code == 200
    assert trends_res.get_json()['success'] is True

    # ---------------------------------------------------------
    # 7. Expenses & Insurance
    # ---------------------------------------------------------
    exp_res = client.post('/api/expenses/', json={
        'family_member_id': member_a_id,
        'amount': 2500.00,
        'category': 'Doctor Visits',
        'expense_date': '2026-05-10',
        'hospital': 'Apollo Hospital',
        'description': 'Executive Health Checkup Fee'
    })
    assert exp_res.status_code == 200

    # Expense summary
    exp_sum = client.get('/api/expenses/summary')
    assert exp_sum.status_code == 200
    sum_data = exp_sum.get_json()['data']
    assert sum_data['total'] >= 2500.00

    # Insurance policy & claim
    pol_res = client.post('/api/insurance/policies', json={
        'policy_name': 'Optima Restore Family Floater',
        'policy_number': 'HDFC-ERGO-2026-99',
        'provider_name': 'HDFC ERGO',
        'family_member_id': member_a_id,
        'sum_insured': 1000000,
        'premium_amount': 22000,
        'valid_from': '2026-01-01',
        'valid_till': '2026-12-31'
    })
    assert pol_res.status_code == 200
    policy_id = pol_res.get_json()['data']['id']

    claim_res = client.post('/api/insurance/claims', json={
        'policy_id': policy_id,
        'claim_number': 'CLM-2026-001',
        'claim_date': '2026-05-12',
        'amount': 2500.00,
        'hospital': 'Apollo Hospital',
        'status': 'submitted',
        'description': 'Outpatient reimbursement claim'
    })
    assert claim_res.status_code == 200

    # ---------------------------------------------------------
    # 8. Timeline, Emergency & Search
    # ---------------------------------------------------------
    timeline_res = client.get(f'/api/timeline?member_id={member_a_id}')
    assert timeline_res.status_code == 200
    events = timeline_res.get_json()['data']
    assert len(events) >= 3

    emerg_res = client.get('/api/emergency/all')
    assert emerg_res.status_code == 200
    emerg_data = emerg_res.get_json()['data']
    assert len(emerg_data) >= 1

    search_res = client.get('/api/search?q=Apollo')
    assert search_res.status_code == 200
    search_data = search_res.get_json()['data']
    assert len(search_data.get('medical_records', [])) >= 1


    # ---------------------------------------------------------
    # 9. Exports
    # ---------------------------------------------------------
    backup_res = client.get('/api/export/backup')
    assert backup_res.status_code == 200
    assert backup_res.headers['Content-Type'].startswith('application/json')
    backup_data = json.loads(backup_res.data.decode('utf-8'))
    assert 'family_members' in backup_data
    assert 'medical_records' in backup_data
    assert len(backup_data['family_members']) >= 1

    csv_res = client.get('/api/export/csv/expenses')
    assert csv_res.status_code == 200
    assert 'Date,Amount,Category' in csv_res.data.decode('utf-8')

    summary_res = client.get(f'/api/export/family-summary/{member_a_id}')
    assert summary_res.status_code == 200
    assert summary_res.headers['Content-Type'].startswith('application/json')

    # ---------------------------------------------------------
    # 10. Dashboard Metrics Consistency
    # ---------------------------------------------------------
    dash_res = client.get('/api/dashboard/summary')
    assert dash_res.status_code == 200
    dash_data = dash_res.get_json()['data']
    assert dash_data['total_family_members'] == 2
    assert dash_data['active_medicines'] == 1
    assert dash_data['upcoming_appointments'] == 1

    # Clean up created document from disk
    client.delete(f'/api/documents/{doc_id}')


def test_multi_user_isolation(client):
    # Register User A
    client.post('/api/auth/register', json={
        'name': 'User A',
        'email': 'user.a@isolation.test',
        'password': 'Password@123'
    })
    client.post('/api/auth/login', json={
        'email': 'user.a@isolation.test',
        'password': 'Password@123'
    })

    # User A creates a private family member & record
    res_mem = client.post('/api/family-members/', json={
        'name': 'Private Family Member A',
        'relationship': 'Daughter'
    })
    member_a_id = res_mem.get_json()['data']['id']

    res_rec = client.post('/api/records/', json={
        'family_member_id': member_a_id,
        'title': 'Confidential Lab Report',
        'record_type': 'Blood Test',
        'record_date': '2026-06-01'
    })
    record_a_id = res_rec.get_json()['data']['id']

    # Logout User A
    client.post('/api/auth/logout')

    # Register & Login User B
    client.post('/api/auth/register', json={
        'name': 'User B',
        'email': 'user.b@isolation.test',
        'password': 'Password@123'
    })
    client.post('/api/auth/login', json={
        'email': 'user.b@isolation.test',
        'password': 'Password@123'
    })

    # User B attempts to read User A's family member -> 404
    get_mem = client.get(f'/api/family-members/{member_a_id}')
    assert get_mem.status_code == 404

    # User B attempts to update User A's family member -> 404
    put_mem = client.put(f'/api/family-members/{member_a_id}', json={'name': 'Hacked'})
    assert put_mem.status_code == 404

    # User B attempts to delete User A's family member -> 404
    del_mem = client.delete(f'/api/family-members/{member_a_id}')
    assert del_mem.status_code == 404

    # User B attempts to read User A's medical record -> 404
    get_rec = client.get(f'/api/records/{record_a_id}')
    assert get_rec.status_code == 404

    # User B's list of members must not contain User A's member
    b_members = client.get('/api/family-members/').get_json()['data']
    assert all(m['id'] != member_a_id for m in b_members)

    # User B's export backup must not contain User A's records
    b_backup = json.loads(client.get('/api/export/backup').data.decode('utf-8'))
    assert len(b_backup['family_members']) == 0
    assert len(b_backup['medical_records']) == 0


def test_security_and_edge_cases(client):
    # Unauthorized requests to protected routes -> 401 or redirect to login
    client.post('/api/auth/logout')
    unauth_res = client.get('/api/family-members/')
    assert unauth_res.status_code == 401 or unauth_res.status_code == 302

    # Login as tester
    client.post('/api/auth/register', json={
        'name': 'Edge Tester',
        'email': 'edge@tester.test',
        'password': 'Password@123'
    })
    client.post('/api/auth/login', json={
        'email': 'edge@tester.test',
        'password': 'Password@123'
    })

    # SQL Injection payload test
    sqli_search = client.get("/api/search?q=' OR '1'='1")
    assert sqli_search.status_code == 200
    # Parameterized query should safely search for literal string without crashing or dumping DB
    assert isinstance(sqli_search.get_json()['data'], dict)
    assert 'medical_records' in sqli_search.get_json()['data']


    # Nonexistent record IDs -> 404
    assert client.get('/api/family-members/99999').status_code == 404
    assert client.get('/api/records/99999').status_code == 404
    assert client.get('/api/medicines/99999').status_code == 404
    assert client.get('/api/appointments/99999').status_code == 404
    assert client.get('/api/tests/99999').status_code == 404
    assert client.get('/api/vaccinations/99999').status_code == 404
    assert client.get('/api/expenses/99999').status_code == 404
    assert client.get('/api/documents/99999').status_code == 404
