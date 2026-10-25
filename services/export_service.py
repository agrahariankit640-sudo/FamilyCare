import json
import csv
from io import StringIO
from models.db import get_db

def export_backup_json(user_id):
    db = get_db()
    backup = {}
    
    tables = [
        'family_members', 'medical_records', 'medicines', 'medicine_reminders',
        'doctor_visits', 'tests', 'vaccinations', 'health_parameters',
        'expenses', 'insurance_policies', 'insurance_claims'
    ]
    
    for table in tables:
        rows = db.execute(f"SELECT * FROM {table} WHERE user_id = ?", (user_id,)).fetchall()
        backup[table] = [dict(row) for row in rows]
        
    return json.dumps(backup, indent=2, default=str)

def export_csv(user_id, module, filters=None):
    db = get_db()
    output = StringIO()
    writer = csv.writer(output)
    
    mod = str(module).lower()
    if mod in ['expenses', 'expense']:
        rows = db.execute("SELECT expense_date, amount, category, hospital, description FROM expenses WHERE user_id = ? ORDER BY expense_date DESC", (user_id,)).fetchall()
        writer.writerow(['Date', 'Amount', 'Category', 'Hospital', 'Description'])
    elif mod in ['medical_records', 'records', 'record']:
        rows = db.execute("SELECT record_date, title, record_type, doctor, diagnosis, hospital FROM medical_records WHERE user_id = ? ORDER BY record_date DESC", (user_id,)).fetchall()
        writer.writerow(['Date', 'Title', 'Type', 'Doctor', 'Diagnosis', 'Hospital'])
    elif mod in ['medicines', 'medicine', 'meds']:
        rows = db.execute("SELECT name, dosage, frequency, start_date, end_date, status, doctor_prescribed FROM medicines WHERE user_id = ? ORDER BY created_at DESC", (user_id,)).fetchall()
        writer.writerow(['Name', 'Dosage', 'Frequency', 'Start Date', 'End Date', 'Status', 'Doctor'])
    elif mod in ['appointments', 'visits', 'doctor_visits']:
        rows = db.execute("SELECT doctor_name, specialty, hospital, visit_date, visit_time, reason, status FROM doctor_visits WHERE user_id = ? ORDER BY visit_date DESC", (user_id,)).fetchall()
        writer.writerow(['Doctor Name', 'Specialty', 'Hospital', 'Date', 'Time', 'Reason', 'Status'])
    elif mod in ['tests', 'labs']:
        rows = db.execute("SELECT test_name, test_date, laboratory, result, status FROM tests WHERE user_id = ? ORDER BY test_date DESC", (user_id,)).fetchall()
        writer.writerow(['Test Name', 'Date', 'Laboratory', 'Result', 'Status'])
    elif mod in ['vaccinations', 'vaccine']:
        rows = db.execute("SELECT vaccine_name, date_administered, dose_number, hospital_name, next_due_date FROM vaccinations WHERE user_id = ? ORDER BY date_administered DESC", (user_id,)).fetchall()
        writer.writerow(['Vaccine Name', 'Date Administered', 'Dose', 'Hospital/Provider', 'Next Due Date'])
    elif mod in ['health_parameters', 'vitals', 'parameters']:
        rows = db.execute("SELECT parameter_name, value, unit, record_date, record_time FROM health_parameters WHERE user_id = ? ORDER BY record_date DESC, record_time DESC", (user_id,)).fetchall()
        writer.writerow(['Parameter', 'Value', 'Unit', 'Record Date', 'Record Time'])
    else:
        return None
        
    for row in rows:
        writer.writerow(list(row))
        
    return output.getvalue()

def export_family_summary(user_id, member_id):
    db = get_db()
    summary = {}
    
    member = db.execute("SELECT * FROM family_members WHERE id = ? AND user_id = ?", (member_id, user_id)).fetchone()
    if not member:
        return None
        
    summary['profile'] = dict(member)
    summary['conditions'] = member['existing_conditions']
    summary['allergies'] = member['allergies']
    
    meds = db.execute("SELECT name, dosage, frequency, status FROM medicines WHERE family_member_id = ? AND user_id = ?", (member_id, user_id)).fetchall()
    summary['medicines'] = [dict(row) for row in meds]
    
    vitals = db.execute("SELECT parameter_name, value, unit, record_date, record_time FROM health_parameters WHERE family_member_id = ? AND user_id = ? ORDER BY record_date DESC, record_time DESC LIMIT 10", (member_id, user_id)).fetchall()
    summary['recent_vitals'] = [dict(row) for row in vitals]
    
    return summary


