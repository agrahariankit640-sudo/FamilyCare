from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from models.test_record import TestRecord
from models.audit_log import AuditLog

tests_bp = Blueprint('tests', __name__)

@tests_bp.route('/', methods=['GET'])
@login_required
def get_all():
    try:
        member_id = request.args.get('family_member_id') or request.args.get('member_id')
        if member_id and str(member_id).isdigit():
            member_id = int(member_id)
        else:
            member_id = None
        filter_type = request.args.get('filter') or request.args.get('tab')
        if filter_type and 'pending' in filter_type.lower():
            items = TestRecord.get_pending_followups(current_user.id)
        else:
            items = TestRecord.get_all(current_user.id, member_id=member_id)
        return jsonify({'success': True, 'data': items})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@tests_bp.route('/', methods=['POST'])
@login_required
def create():
    try:
        data = request.json
        item_id = TestRecord.create(current_user.id, data)
        if item_id:
            AuditLog.log(current_user.id, 'create_testrecord', f'Created TestRecord {item_id}')
            return jsonify({'success': True, 'data': {'id': item_id}})
        return jsonify({'error': 'Creation failed'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@tests_bp.route('/<int:id>', methods=['GET'])
@login_required
def get(id):
    try:
        item = TestRecord.get_by_id(id, current_user.id)
        if item:
            return jsonify({'success': True, 'data': item})
        return jsonify({'error': 'Not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@tests_bp.route('/<int:id>', methods=['PUT'])
@login_required
def update(id):
    try:
        data = request.json
        success = TestRecord.update(id, current_user.id, data)
        if success:
            AuditLog.log(current_user.id, 'update_testrecord', f'Updated TestRecord {id}')
            return jsonify({'success': True})
        return jsonify({'error': 'Update failed'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@tests_bp.route('/<int:id>', methods=['DELETE'])
@login_required
def delete(id):
    try:
        success = TestRecord.delete(id, current_user.id)
        if success:
            AuditLog.log(current_user.id, 'delete_testrecord', f'Deleted TestRecord {id}')
            return jsonify({'success': True})
        return jsonify({'error': 'Deletion failed'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500
