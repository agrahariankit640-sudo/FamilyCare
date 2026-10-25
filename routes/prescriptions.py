from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from models.prescription import Prescription
from models.audit_log import AuditLog

prescriptions_bp = Blueprint('prescriptions', __name__)

@prescriptions_bp.route('/', methods=['GET'])
@login_required
def get_all():
    try:
        member_id = request.args.get('member_id') or request.args.get('family_member_id')
        items = Prescription.get_all(current_user.id, member_id)
        return jsonify({'success': True, 'data': [dict(item) for item in items]})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@prescriptions_bp.route('/', methods=['POST'])
@login_required
def create():
    try:
        data = request.json or {}
        item_id = Prescription.create(current_user.id, data)
        if item_id:
            AuditLog.log(current_user.id, 'create_prescription', 'prescriptions', item_id, f'Created Prescription {item_id}')
            return jsonify({'success': True, 'data': {'id': item_id}})
        return jsonify({'error': 'Creation failed'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@prescriptions_bp.route('/<int:id>', methods=['GET'])
@login_required
def get(id):
    try:
        item = Prescription.get_by_id(id, current_user.id)
        if item:
            return jsonify({'success': True, 'data': dict(item)})
        return jsonify({'error': 'Not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@prescriptions_bp.route('/<int:id>', methods=['PUT'])
@login_required
def update(id):
    try:
        data = request.json or {}
        success = Prescription.update(id, current_user.id, data)
        if success:
            AuditLog.log(current_user.id, 'update_prescription', 'prescriptions', id, f'Updated Prescription {id}')
            return jsonify({'success': True})
        return jsonify({'error': 'Update failed'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@prescriptions_bp.route('/<int:id>', methods=['DELETE'])
@login_required
def delete(id):
    try:
        success = Prescription.delete(id, current_user.id)
        if success:
            AuditLog.log(current_user.id, 'delete_prescription', 'prescriptions', id, f'Deleted Prescription {id}')
            return jsonify({'success': True})
        return jsonify({'error': 'Deletion failed'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

