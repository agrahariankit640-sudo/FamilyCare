from models.db import get_db

def search_all(user_id, query='', filters=None):
    results = {
        'medical_records': [],
        'medicines': [],
        'appointments': [],
        'tests': [],
        'vaccinations': []
    }
    
    db = get_db()
    query = (query or '').strip()
    search_term = f"%{query}%" if query else None
    
    member_id = None
    if filters:
        if hasattr(filters, 'get'):
            m_val = filters.get('family_member_id')
        elif isinstance(filters, dict):
            m_val = filters.get('family_member_id')
        else:
            m_val = None
        if m_val:
            try:
                member_id = int(m_val)
            except (ValueError, TypeError):
                member_id = None

    # 1. Medical records
    rec_sql = '''
        SELECT r.id, r.title, r.record_date as date, r.record_type, r.description, r.doctor, r.hospital, r.family_member_id, fm.name as member_name
        FROM medical_records r
        LEFT JOIN family_members fm ON r.family_member_id = fm.id
        WHERE r.user_id = ?
    '''
    rec_params = [user_id]
    if member_id:
        rec_sql += ' AND r.family_member_id = ?'
        rec_params.append(member_id)
    if search_term:
        rec_sql += ' AND (r.title LIKE ? OR r.diagnosis LIKE ? OR r.notes LIKE ? OR r.description LIKE ? OR r.doctor LIKE ? OR r.hospital LIKE ? OR fm.name LIKE ?)'
        rec_params.extend([search_term] * 7)
    rec_sql += ' ORDER BY r.record_date DESC LIMIT 50'
    rec_rows = db.execute(rec_sql, rec_params).fetchall()
    results['medical_records'] = [dict(row) for row in rec_rows]

    # 2. Medicines
    med_sql = '''
        SELECT m.id, m.name as title, m.dosage, m.status, m.start_date as date, m.doctor, m.family_member_id, fm.name as member_name, m.instructions as description
        FROM medicines m
        LEFT JOIN family_members fm ON m.family_member_id = fm.id
        WHERE m.user_id = ?
    '''
    med_params = [user_id]
    if member_id:
        med_sql += ' AND m.family_member_id = ?'
        med_params.append(member_id)
    if search_term:
        med_sql += ' AND (m.name LIKE ? OR m.instructions LIKE ? OR m.notes LIKE ? OR m.doctor LIKE ? OR fm.name LIKE ?)'
        med_params.extend([search_term] * 5)
    med_sql += ' ORDER BY m.start_date DESC LIMIT 50'
    med_rows = db.execute(med_sql, med_params).fetchall()
    results['medicines'] = [dict(row) for row in med_rows]

    # 3. Appointments
    appt_sql = '''
        SELECT a.id, a.doctor_name as title, a.visit_date as date, a.reason as description, a.hospital, a.family_member_id, fm.name as member_name, a.doctor_name as doctor
        FROM doctor_visits a
        LEFT JOIN family_members fm ON a.family_member_id = fm.id
        WHERE a.user_id = ?
    '''
    appt_params = [user_id]
    if member_id:
        appt_sql += ' AND a.family_member_id = ?'
        appt_params.append(member_id)
    if search_term:
        appt_sql += ' AND (a.doctor_name LIKE ? OR a.reason LIKE ? OR a.hospital LIKE ? OR a.specialization LIKE ? OR a.notes LIKE ? OR fm.name LIKE ?)'
        appt_params.extend([search_term] * 6)
    appt_sql += ' ORDER BY a.visit_date DESC LIMIT 50'
    appt_rows = db.execute(appt_sql, appt_params).fetchall()
    results['appointments'] = [dict(row) for row in appt_rows]

    # 4. Tests
    test_sql = '''
        SELECT t.id, t.test_name as title, t.test_date as date, t.result_summary as description, t.doctor, t.family_member_id, fm.name as member_name
        FROM tests t
        LEFT JOIN family_members fm ON t.family_member_id = fm.id
        WHERE t.user_id = ?
    '''
    test_params = [user_id]
    if member_id:
        test_sql += ' AND t.family_member_id = ?'
        test_params.append(member_id)
    if search_term:
        test_sql += ' AND (t.test_name LIKE ? OR t.result_summary LIKE ? OR t.doctor LIKE ? OR t.notes LIKE ? OR fm.name LIKE ?)'
        test_params.extend([search_term] * 5)
    test_sql += ' ORDER BY t.test_date DESC LIMIT 50'
    test_rows = db.execute(test_sql, test_params).fetchall()
    results['tests'] = [dict(row) for row in test_rows]

    # 5. Vaccinations
    vax_sql = '''
        SELECT v.id, v.vaccine_name as title, v.vaccination_date as date, v.hospital, v.family_member_id, fm.name as member_name, v.dose_number, v.notes as description
        FROM vaccinations v
        LEFT JOIN family_members fm ON v.family_member_id = fm.id
        WHERE v.user_id = ?
    '''
    vax_params = [user_id]
    if member_id:
        vax_sql += ' AND v.family_member_id = ?'
        vax_params.append(member_id)
    if search_term:
        vax_sql += ' AND (v.vaccine_name LIKE ? OR v.hospital LIKE ? OR v.notes LIKE ? OR fm.name LIKE ?)'
        vax_params.extend([search_term] * 4)
    vax_sql += ' ORDER BY v.vaccination_date DESC LIMIT 50'
    vax_rows = db.execute(vax_sql, vax_params).fetchall()
    results['vaccinations'] = [dict(row) for row in vax_rows]

    return results
