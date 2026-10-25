from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from models.family_member import FamilyMember
from models.audit_log import AuditLog

family_bp = Blueprint('family', __name__)

@family_bp.route('/', methods=['GET'])
@login_required
def get_all():
    try:
        members = FamilyMember.get_all(current_user.id)
        return jsonify({'success': True, 'data': members})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@family_bp.route('/', methods=['POST'])
@login_required
def create():
    try:
        data = request.json or {}
        if not data.get('name'):
            return jsonify({'error': 'Name is required'}), 400
        member_id = FamilyMember.create(current_user.id, data)
        if member_id:
            AuditLog.log(current_user.id, 'create_family_member', f'Created family member {member_id}')
            return jsonify({'success': True, 'data': {'id': member_id}})
        return jsonify({'error': 'Creation failed'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@family_bp.route('/<int:id>', methods=['GET'])
@login_required
def get(id):
    try:
        member = FamilyMember.get_by_id(id, current_user.id)
        if member:
            return jsonify({'success': True, 'data': member})
        return jsonify({'error': 'Not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@family_bp.route('/<int:id>', methods=['PUT'])
@login_required
def update(id):
    try:
        data = request.json or {}
        success = FamilyMember.update(id, current_user.id, data)
        if success:
            AuditLog.log(current_user.id, 'update_family_member', f'Updated family member {id}')
            return jsonify({'success': True})
        return jsonify({'error': 'Update failed or not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@family_bp.route('/<int:id>', methods=['DELETE'])
@login_required
def delete(id):
    try:
        success = FamilyMember.delete(id, current_user.id)
        if success:
            AuditLog.log(current_user.id, 'delete_family_member', 'family_members', id, f'Deleted family member {id}')
            return jsonify({'success': True})
        return jsonify({'error': 'Deletion failed or not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@family_bp.route('/<int:id>/archive', methods=['PUT', 'POST'])
@login_required
def archive(id):
    try:
        success = FamilyMember.archive(id, current_user.id)
        if success:
            AuditLog.log(current_user.id, 'archive_family_member', 'family_members', id, f'Archived family member {id}')
            return jsonify({'success': True, 'message': 'Member archived'})
        return jsonify({'error': 'Member not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@family_bp.route('/<int:id>/summary', methods=['GET'])
@login_required
def summary(id):
    try:
        from models.db import get_db
        db = get_db()
        
        # Latest BP
        bp_row = db.execute('''
            SELECT value, unit, record_date FROM health_parameters 
            WHERE family_member_id = ? AND user_id = ? AND LOWER(parameter_name) LIKE '%pressure%' 
            ORDER BY record_date DESC, record_time DESC LIMIT 1
        ''', (id, current_user.id)).fetchone()
        latest_bp = f"{bp_row['value']} {bp_row['unit'] or 'mmHg'}" if bp_row else '--/--'
        
        # Active Medicines
        meds_count = db.execute('''
            SELECT COUNT(*) as count FROM medicines 
            WHERE family_member_id = ? AND user_id = ? AND LOWER(status) = 'active'
        ''', (id, current_user.id)).fetchone()['count']
        
        # Next Appointment
        appt_row = db.execute('''
            SELECT doctor_name, visit_date, hospital FROM doctor_visits 
            WHERE family_member_id = ? AND user_id = ? AND visit_date >= date('now') 
            ORDER BY visit_date ASC LIMIT 1
        ''', (id, current_user.id)).fetchone()
        next_appt = f"Dr. {appt_row['doctor_name']} ({appt_row['visit_date']})" if appt_row else 'None scheduled'
        
        # Tests count
        tests_count = db.execute('''
            SELECT COUNT(*) as count FROM tests 
            WHERE family_member_id = ? AND user_id = ?
        ''', (id, current_user.id)).fetchone()['count']
        
        return jsonify({
            'success': True,
            'data': {
                'bp': latest_bp,
                'active_medicines': meds_count,
                'next_appointment': next_appt,
                'tests_count': tests_count
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@family_bp.route('/<int:id>/photo', methods=['POST'])
@login_required
def photo(id):
    try:
        if 'photo' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        file = request.files['photo']
        from services.file_service import save_file
        path = save_file(file, 'member_photos')
        if path:
            FamilyMember.update(id, current_user.id, {'photo': path})
            AuditLog.log(current_user.id, 'update_family_member_photo', f'Updated photo for family member {id}')
            return jsonify({'success': True, 'data': {'path': path}})
        return jsonify({'error': 'Upload failed'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500
