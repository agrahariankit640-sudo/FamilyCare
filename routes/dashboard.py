from flask import Blueprint, jsonify
from flask_login import login_required, current_user
from models.family_member import FamilyMember
from models.medicine import Medicine
from models.appointment import Appointment
from models.test_record import TestRecord
from models.medical_record import MedicalRecord
from models.vaccination import Vaccination
from models.expense import Expense
from models.audit_log import AuditLog

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/summary', methods=['GET'])
@login_required
def summary():
    try:
        data = {
            'total_family_members': FamilyMember.get_count(current_user.id),
            'active_medicines': Medicine.get_active_count(current_user.id),
            'upcoming_appointments': Appointment.get_upcoming_count(current_user.id),
            'pending_followups': len(TestRecord.get_pending_followups(current_user.id)),
            'recent_records_count': len(MedicalRecord.get_recent(current_user.id)),
            'upcoming_vaccinations': len(Vaccination.get_upcoming(current_user.id)),
            'monthly_expenses': Expense.get_total(current_user.id)
        }
        return jsonify({'success': True, 'data': data})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@dashboard_bp.route('/recent-activity', methods=['GET'])
@login_required
def recent_activity():
    try:
        logs = AuditLog.get_by_user(current_user.id)
        return jsonify({'success': True, 'data': logs[:10]})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@dashboard_bp.route('/upcoming', methods=['GET'])
@login_required
def upcoming():
    try:
        events = []
        appts = Appointment.get_all(current_user.id, status='upcoming')
        for a in appts:
            events.append({
                'title': f"Dr. {a['doctor_name']} ({a['specialization'] or 'Consultation'})",
                'date': a['visit_date'],
                'type': 'appointment',
                'member': a['member_name']
            })
        vaccs = Vaccination.get_upcoming(current_user.id)
        for v in vaccs:
            events.append({
                'title': f"Vaccine: {v['vaccine_name']}",
                'date': v['next_due_date'],
                'type': 'vaccination',
                'member': v.get('member_name', '')
            })
        return jsonify({'success': True, 'data': events})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
