import os
import time
from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user, logout_user
from models.user import User
from models.audit_log import AuditLog

users_bp = Blueprint('users', __name__)

@users_bp.route('/me', methods=['GET'])
@login_required
def me():
    try:
        user = User.get_by_id(current_user.id)
        if user:
            u_dict = dict(user)
            u_dict.pop('password_hash', None)
            return jsonify({'success': True, 'data': u_dict})
        return jsonify({'error': 'User not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@users_bp.route('/settings', methods=['PUT'])
@login_required
def settings():
    try:
        data = request.json or {}
        success = User.update(current_user.id, data)
        if success:
            AuditLog.log(current_user.id, 'update_settings', 'users', current_user.id, 'User updated settings')
            return jsonify({'success': True, 'message': 'Profile settings updated'})
        return jsonify({'error': 'Update failed'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@users_bp.route('/photo', methods=['POST'])
@login_required
def upload_photo():
    try:
        file = request.files.get('photo') or request.files.get('file')
        if not file or not file.filename:
            return jsonify({'error': 'No file selected'}), 400
        
        ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
        if ext not in ['jpg', 'jpeg', 'png', 'gif', 'webp']:
            return jsonify({'error': 'Invalid image format. Allowed: JPG, PNG, GIF, WEBP'}), 400
            
        avatar_dir = os.path.join(current_app.root_path, 'static', 'uploads', 'avatars')
        os.makedirs(avatar_dir, exist_ok=True)
        
        filename = f"user_{current_user.id}_{int(time.time())}.{ext}"
        filepath = os.path.join(avatar_dir, filename)
        file.save(filepath)
        
        photo_url = f"/static/uploads/avatars/{filename}"
        User.update_photo(current_user.id, photo_url)
        AuditLog.log(current_user.id, 'update_photo', 'users', current_user.id, 'User updated profile photo')
        return jsonify({'success': True, 'photo_url': photo_url})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@users_bp.route('/photo', methods=['DELETE'])
@login_required
def delete_photo():
    try:
        User.update_photo(current_user.id, None)
        AuditLog.log(current_user.id, 'delete_photo', 'users', current_user.id, 'User removed profile photo')
        return jsonify({'success': True, 'message': 'Profile photo removed'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@users_bp.route('/account', methods=['DELETE'])
@login_required
def account():
    try:
        data = request.json or {}
        if data.get('confirm') != 'yes' and data.get('confirm') is not True:
            return jsonify({'error': 'Confirmation required'}), 400
        uid = current_user.id
        AuditLog.log(uid, 'delete_account', 'users', uid, 'User deleted their account')
        User.delete(uid)
        logout_user()
        return jsonify({'success': True, 'message': 'Account deleted successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
