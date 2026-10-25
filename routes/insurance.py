from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from models.insurance import InsurancePolicy
from models.insurance_claim import InsuranceClaim
from models.audit_log import AuditLog

insurance_bp = Blueprint('insurance', __name__)

@insurance_bp.route('/policies', methods=['GET'])
@login_required
def get_all_policies():
    try:
        items = InsurancePolicy.get_all_policies(current_user.id)
        return jsonify({'success': True, 'data': items})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@insurance_bp.route('/policies', methods=['POST'])
@login_required
def create_policy():
    try:
        data = request.json
        item_id = InsurancePolicy.create_policy(current_user.id, data)
        if item_id:
            AuditLog.log(current_user.id, 'create_policy', f'Created policy {item_id}')
            return jsonify({'success': True, 'data': {'id': item_id}})
        return jsonify({'error': 'Creation failed'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@insurance_bp.route('/policies/<int:id>', methods=['GET'])
@login_required
def get_policy(id):
    try:
        item = InsurancePolicy.get_policy_by_id(id, current_user.id)
        if item:
            return jsonify({'success': True, 'data': item})
        return jsonify({'error': 'Not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@insurance_bp.route('/policies/<int:id>', methods=['PUT'])
@login_required
def update_policy(id):
    try:
        data = request.json
        success = InsurancePolicy.update_policy(id, current_user.id, data)
        if success:
            AuditLog.log(current_user.id, 'update_policy', f'Updated policy {id}')
            return jsonify({'success': True})
        return jsonify({'error': 'Update failed'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@insurance_bp.route('/policies/<int:id>', methods=['DELETE'])
@login_required
def delete_policy(id):
    try:
        success = InsurancePolicy.delete_policy(id, current_user.id)
        if success:
            AuditLog.log(current_user.id, 'delete_policy', f'Deleted policy {id}')
            return jsonify({'success': True})
        return jsonify({'error': 'Deletion failed'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@insurance_bp.route('/claims', methods=['GET'])
@login_required
def get_all_claims():
    try:
        items = InsuranceClaim.get_all(current_user.id)
        return jsonify({'success': True, 'data': items})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@insurance_bp.route('/claims', methods=['POST'])
@login_required
def create_claim():
    try:
        data = request.json
        item_id = InsuranceClaim.create(current_user.id, data)
        if item_id:
            AuditLog.log(current_user.id, 'create_claim', f'Created claim {item_id}')
            return jsonify({'success': True, 'data': {'id': item_id}})
        return jsonify({'error': 'Creation failed'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@insurance_bp.route('/claims/<int:id>', methods=['GET'])
@login_required
def get_claim(id):
    try:
        item = InsuranceClaim.get_by_id(id, current_user.id)
        if item:
            return jsonify({'success': True, 'data': item})
        return jsonify({'error': 'Not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@insurance_bp.route('/claims/<int:id>', methods=['PUT'])
@login_required
def update_claim(id):
    try:
        data = request.json
        success = InsuranceClaim.update(id, current_user.id, data)
        if success:
            AuditLog.log(current_user.id, 'update_claim', f'Updated claim {id}')
            return jsonify({'success': True})
        return jsonify({'error': 'Update failed'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@insurance_bp.route('/claims/<int:id>', methods=['DELETE'])
@login_required
def delete_claim(id):
    try:
        success = InsuranceClaim.delete(id, current_user.id)
        if success:
            AuditLog.log(current_user.id, 'delete_claim', f'Deleted claim {id}')
            return jsonify({'success': True})
        return jsonify({'error': 'Deletion failed'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500
