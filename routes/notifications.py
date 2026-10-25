from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from models.notification import Notification

notifications_bp = Blueprint('notifications', __name__)

@notifications_bp.route('/', methods=['GET'])
@login_required
def get_all():
    try:
        items = Notification.get_all(current_user.id)
        return jsonify({'success': True, 'data': items})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@notifications_bp.route('/unread-count', methods=['GET'])
@login_required
def get_unread_count():
    try:
        count = Notification.get_unread_count(current_user.id)
        return jsonify({'success': True, 'data': {'count': count}})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@notifications_bp.route('/<int:id>/read', methods=['PUT'])
@login_required
def mark_read(id):
    try:
        success = Notification.mark_read(id, current_user.id)
        if success:
            return jsonify({'success': True})
        return jsonify({'error': 'Update failed'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@notifications_bp.route('/read-all', methods=['PUT'])
@login_required
def mark_all_read():
    try:
        success = Notification.mark_all_read(current_user.id)
        if success:
            return jsonify({'success': True})
        return jsonify({'error': 'Update failed'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@notifications_bp.route('/<int:id>', methods=['DELETE'])
@login_required
def delete(id):
    try:
        success = Notification.delete(id, current_user.id)
        if success:
            return jsonify({'success': True})
        return jsonify({'error': 'Deletion failed'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500
