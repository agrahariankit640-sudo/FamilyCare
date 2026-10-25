from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from models.medicine import Medicine
from models.audit_log import AuditLog

medicines_bp = Blueprint('medicines', __name__)

@medicines_bp.route('/', methods=['GET'])
@login_required
def get_all():
    try:
        items = Medicine.get_all(current_user.id)
        return jsonify({'success': True, 'data': items})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@medicines_bp.route('/', methods=['POST'])
@login_required
def create():
    try:
        data = request.json
        item_id = Medicine.create(current_user.id, data)
        if item_id:
            AuditLog.log(current_user.id, 'create_medicine', f'Created Medicine {item_id}')
            return jsonify({'success': True, 'data': {'id': item_id}})
        return jsonify({'error': 'Creation failed'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@medicines_bp.route('/<int:id>', methods=['GET'])
@login_required
def get(id):
    try:
        item = Medicine.get_by_id(id, current_user.id)
        if item:
            return jsonify({'success': True, 'data': item})
        return jsonify({'error': 'Not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@medicines_bp.route('/<int:id>', methods=['PUT'])
@login_required
def update(id):
    try:
        data = request.json
        success = Medicine.update(id, current_user.id, data)
        if success:
            AuditLog.log(current_user.id, 'update_medicine', f'Updated Medicine {id}')
            return jsonify({'success': True})
        return jsonify({'error': 'Update failed'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@medicines_bp.route('/<int:id>', methods=['DELETE'])
@login_required
def delete(id):
    try:
        success = Medicine.delete(id, current_user.id)
        if success:
            AuditLog.log(current_user.id, 'delete_medicine', f'Deleted Medicine {id}')
            return jsonify({'success': True})
        return jsonify({'error': 'Deletion failed'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@medicines_bp.route('/<int:id>/status', methods=['PUT'])
@login_required
def update_status(id):
    try:
        data = request.json
        success = Medicine.update_status(id, current_user.id, data.get('status'))
        if success:
            AuditLog.log(current_user.id, 'update_medicine', f'Updated Medicine {id} status')
            return jsonify({'success': True})
        return jsonify({'error': 'Update failed'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500
