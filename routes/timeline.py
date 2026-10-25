from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from models.db import get_db

timeline_bp = Blueprint('timeline', __name__)

@timeline_bp.route('/', methods=['GET'])
@login_required
def get_timeline():
    try:
        user_id = current_user.id
        member_id = request.args.get('family_member_id') or request.args.get('member_id')
        event_type = request.args.get('type')
        date_from = request.args.get('date_from') or request.args.get('from_date')
        date_to = request.args.get('date_to') or request.args.get('to_date')

        db = get_db()
        events = []

        # 1. Medical Records
        if not event_type or event_type.lower() in ['record', 'medical_record', 'records']:
            query = """
                SELECT r.id, r.title, r.record_type, r.record_date as date, r.doctor, r.hospital,
                       r.description, r.family_member_id, fm.name as member_name
                FROM medical_records r
                LEFT JOIN family_members fm ON r.family_member_id = fm.id
                WHERE r.user_id = ?
            """
            params = [user_id]
            if member_id:
                query += " AND r.family_member_id = ?"
                params.append(member_id)
            if date_from:
                query += " AND r.record_date >= ?"
                params.append(date_from)
            if date_to:
                query += " AND r.record_date <= ?"
                params.append(date_to)

            for row in db.execute(query, params).fetchall():
                events.append({
                    'id': row['id'],
                    'type': 'record',
                    'title': row['title'] or f"{row['record_type'] or 'Medical'} Record",
                    'description': row['description'] or f"Type: {row['record_type'] or 'General'}",
                    'date': row['date'],
                    'doctor': row['doctor'] or row['hospital'] or '',
                    'family_member_id': row['family_member_id'],
                    'member_name': row['member_name'] or 'Family Member',
                    'link': '/records'
                })

        # 2. Medicines
        if not event_type or event_type.lower() in ['medicine', 'medicines']:
            query = """
                SELECT m.id, m.name, m.dosage, m.frequency, m.start_date as date, m.doctor,
                       m.instructions, m.family_member_id, fm.name as member_name
                FROM medicines m
                LEFT JOIN family_members fm ON m.family_member_id = fm.id
                WHERE m.user_id = ? AND m.start_date IS NOT NULL
            """
            params = [user_id]
            if member_id:
                query += " AND m.family_member_id = ?"
                params.append(member_id)
            if date_from:
                query += " AND m.start_date >= ?"
                params.append(date_from)
            if date_to:
                query += " AND m.start_date <= ?"
                params.append(date_to)

            for row in db.execute(query, params).fetchall():
                desc = f"Dosage: {row['dosage'] or 'N/A'}"
                if row['frequency']:
                    desc += f" ({row['frequency']})"
                events.append({
                    'id': row['id'],
                    'type': 'medicine',
                    'title': f"Started: {row['name']}",
                    'description': desc,
                    'date': row['date'],
                    'doctor': row['doctor'] or '',
                    'family_member_id': row['family_member_id'],
                    'member_name': row['member_name'] or 'Family Member',
                    'link': '/medicines'
                })

        # 3. Doctor Visits / Appointments
        if not event_type or event_type.lower() in ['appointment', 'doctor_visit', 'appointments']:
            query = """
                SELECT a.id, a.doctor_name, a.hospital, a.specialization, a.visit_date as date,
                       a.reason, a.status, a.family_member_id, fm.name as member_name
                FROM doctor_visits a
                LEFT JOIN family_members fm ON a.family_member_id = fm.id
                WHERE a.user_id = ?
            """
            params = [user_id]
            if member_id:
                query += " AND a.family_member_id = ?"
                params.append(member_id)
            if date_from:
                query += " AND a.visit_date >= ?"
                params.append(date_from)
            if date_to:
                query += " AND a.visit_date <= ?"
                params.append(date_to)

            for row in db.execute(query, params).fetchall():
                title = f"Visit: Dr. {row['doctor_name']}"
                if row['specialization']:
                    title += f" ({row['specialization']})"
                events.append({
                    'id': row['id'],
                    'type': 'appointment',
                    'title': title,
                    'description': row['reason'] or f"Hospital: {row['hospital'] or 'Clinic'} - Status: {row['status']}",
                    'date': row['date'],
                    'doctor': row['doctor_name'],
                    'family_member_id': row['family_member_id'],
                    'member_name': row['member_name'] or 'Family Member',
                    'link': '/appointments'
                })

        # 4. Lab Tests
        if not event_type or event_type.lower() in ['test', 'tests']:
            query = """
                SELECT t.id, t.test_name, t.test_date as date, t.doctor, t.result_summary,
                       t.family_member_id, fm.name as member_name
                FROM tests t
                LEFT JOIN family_members fm ON t.family_member_id = fm.id
                WHERE t.user_id = ?
            """
            params = [user_id]
            if member_id:
                query += " AND t.family_member_id = ?"
                params.append(member_id)
            if date_from:
                query += " AND t.test_date >= ?"
                params.append(date_from)
            if date_to:
                query += " AND t.test_date <= ?"
                params.append(date_to)

            for row in db.execute(query, params).fetchall():
                events.append({
                    'id': row['id'],
                    'type': 'test',
                    'title': f"Test: {row['test_name']}",
                    'description': f"Result: {row['result_summary'] or 'Pending / Documented'}",
                    'date': row['date'],
                    'doctor': row['doctor'] or '',
                    'family_member_id': row['family_member_id'],
                    'member_name': row['member_name'] or 'Family Member',
                    'link': '/tests'
                })

        # 5. Vaccinations
        if not event_type or event_type.lower() in ['vaccination', 'vaccinations']:
            query = """
                SELECT v.id, v.vaccine_name, v.vaccination_date as date, v.dose_number,
                       v.hospital, v.notes, v.family_member_id, fm.name as member_name
                FROM vaccinations v
                LEFT JOIN family_members fm ON v.family_member_id = fm.id
                WHERE v.user_id = ?
            """
            params = [user_id]
            if member_id:
                query += " AND v.family_member_id = ?"
                params.append(member_id)
            if date_from:
                query += " AND v.vaccination_date >= ?"
                params.append(date_from)
            if date_to:
                query += " AND v.vaccination_date <= ?"
                params.append(date_to)

            for row in db.execute(query, params).fetchall():
                dose_str = f"Dose {row['dose_number']}" if row['dose_number'] else 'Immunization'
                events.append({
                    'id': row['id'],
                    'type': 'vaccination',
                    'title': f"Vaccine: {row['vaccine_name']} ({dose_str})",
                    'description': row['notes'] or f"Hospital: {row['hospital'] or 'Clinic'}",
                    'date': row['date'],
                    'doctor': row['hospital'] or '',
                    'family_member_id': row['family_member_id'],
                    'member_name': row['member_name'] or 'Family Member',
                    'link': '/vaccinations'
                })

        # Sort all chronological events by date descending
        events.sort(key=lambda x: str(x.get('date') or ''), reverse=True)

        return jsonify({'success': True, 'data': events})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
