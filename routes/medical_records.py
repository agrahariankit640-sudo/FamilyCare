from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from models.medical_record import MedicalRecord
from models.audit_log import AuditLog

records_bp = Blueprint('records', __name__)

@records_bp.route('/', methods=['GET'])
@login_required
def get_all():
    try:
        member_id = request.args.get('member_id')
        record_type = request.args.get('record_type')
        filters = {}
        if member_id:
            filters['family_member_id'] = member_id
        if record_type:
            filters['record_type'] = record_type
        records = MedicalRecord.get_all(current_user.id, filters if filters else None)
        return jsonify({'success': True, 'data': [dict(r) for r in records]})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@records_bp.route('/', methods=['POST'])
@login_required
def create():
    try:
        data = request.json
        record_id = MedicalRecord.create(current_user.id, data)
        if record_id:
            AuditLog.log(current_user.id, 'create_medical_record', f'Created medical record {record_id}')
            return jsonify({'success': True, 'data': {'id': record_id}})
        return jsonify({'error': 'Creation failed'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@records_bp.route('/<int:id>', methods=['GET'])
@login_required
def get(id):
    try:
        record = MedicalRecord.get_by_id(id, current_user.id)
        if record:
            return jsonify({'success': True, 'data': dict(record)})
        return jsonify({'error': 'Not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@records_bp.route('/<int:id>', methods=['PUT'])
@login_required
def update(id):
    try:
        data = request.json or {}
        success = MedicalRecord.update(id, current_user.id, data)
        if success:
            AuditLog.log(current_user.id, 'update_medical_record', f'Updated medical record {id}')
            return jsonify({'success': True})
        return jsonify({'error': 'Update failed or not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@records_bp.route('/<int:id>', methods=['DELETE'])
@login_required
def delete(id):
    try:
        success = MedicalRecord.delete(id, current_user.id)
        if success:
            AuditLog.log(current_user.id, 'delete_medical_record', f'Deleted medical record {id}')
            return jsonify({'success': True})
        return jsonify({'error': 'Deletion failed or not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
