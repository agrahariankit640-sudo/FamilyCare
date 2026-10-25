from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from models.reminder import Reminder
from models.audit_log import AuditLog

reminders_bp = Blueprint('reminders', __name__)

from datetime import datetime

@reminders_bp.route('/', methods=['GET'])
@login_required
def get_all():
    try:
        status = request.args.get('status') or request.args.get('tab')
        date = request.args.get('date')
        if status:
            if status.lower() == 'all':
                status = None
            elif status.lower() == 'today':
                status = None
                date = datetime.now().strftime('%Y-%m-%d')
        items = Reminder.get_all(current_user.id, status=status, date=date)
        return jsonify({'success': True, 'data': items})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@reminders_bp.route('/', methods=['POST'])
@login_required
def create():
    try:
        data = request.json
        item_id = Reminder.create(current_user.id, data)
        if item_id:
            AuditLog.log(current_user.id, 'create_reminder', f'Created Reminder {item_id}')
            return jsonify({'success': True, 'data': {'id': item_id}})
        return jsonify({'error': 'Creation failed'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@reminders_bp.route('/<int:id>/status', methods=['PUT'])
@login_required
def update_status(id):
    try:
        data = request.json
        success = Reminder.update_status(id, current_user.id, data.get('status'))
        if success:
            AuditLog.log(current_user.id, 'update_reminder', f'Updated Reminder {id} status')
            return jsonify({'success': True})
        return jsonify({'error': 'Update failed'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@reminders_bp.route('/<int:id>', methods=['DELETE'])
@login_required
def delete(id):
    try:
        success = Reminder.delete(id, current_user.id)
        if success:
            AuditLog.log(current_user.id, 'delete_reminder', f'Deleted Reminder {id}')
            return jsonify({'success': True})
        return jsonify({'error': 'Deletion failed'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500
