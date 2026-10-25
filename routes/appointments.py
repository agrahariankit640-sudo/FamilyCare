from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from models.appointment import Appointment
from models.audit_log import AuditLog

appointments_bp = Blueprint('appointments', __name__)

@appointments_bp.route('/', methods=['GET'])
@login_required
def get_all():
    try:
        member_id = request.args.get('family_member_id') or request.args.get('member_id')
        status = request.args.get('status')
        items = Appointment.get_all(current_user.id, member_id=member_id, status=status)
        return jsonify({'success': True, 'data': items})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@appointments_bp.route('/', methods=['POST'])
@login_required
def create():
    try:
        data = request.json
        item_id = Appointment.create(current_user.id, data)
        if item_id:
            AuditLog.log(current_user.id, 'create_appointment', f'Created Appointment {item_id}')
            return jsonify({'success': True, 'data': {'id': item_id}})
        return jsonify({'error': 'Creation failed'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@appointments_bp.route('/<int:id>', methods=['GET'])
@login_required
def get(id):
    try:
        item = Appointment.get_by_id(id, current_user.id)
        if item:
            return jsonify({'success': True, 'data': item})
        return jsonify({'error': 'Not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@appointments_bp.route('/<int:id>', methods=['PUT'])
@login_required
def update(id):
    try:
        data = request.json
        success = Appointment.update(id, current_user.id, data)
        if success:
            AuditLog.log(current_user.id, 'update_appointment', f'Updated Appointment {id}')
            return jsonify({'success': True})
        return jsonify({'error': 'Update failed'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@appointments_bp.route('/<int:id>', methods=['DELETE'])
@login_required
def delete(id):
    try:
        success = Appointment.delete(id, current_user.id)
        if success:
            AuditLog.log(current_user.id, 'delete_appointment', f'Deleted Appointment {id}')
            return jsonify({'success': True})
        return jsonify({'error': 'Deletion failed'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500
