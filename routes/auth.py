from flask import Blueprint, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from services.auth_service import register_user, authenticate_user, update_profile, change_password
from models.user import User
from models.audit_log import AuditLog
import logging

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.json or {}
        name = data.get('name') or f"{data.get('first_name', '')} {data.get('last_name', '')}".strip()
        email = data.get('email')
        phone = data.get('phone', '')
        password = data.get('password')
        
        if not name or not email or not password:
            return jsonify({'error': 'Name, email, and password are required'}), 400

        user_id, error = register_user(name, email, phone, password)
        if user_id:
            AuditLog.log(user_id, 'register', 'User registered')
            return jsonify({'success': True, 'data': {'id': user_id}}), 201
        return jsonify({'error': error or 'Registration failed'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.json or {}
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400

        user, error = authenticate_user(email, password)
        if user:
            from models.user import UserLogin
            login_user(UserLogin(user))
            AuditLog.log(user['id'], 'login', 'User logged in')
            user_dict = dict(user)
            if 'password_hash' in user_dict:
                del user_dict['password_hash']
            return jsonify({'success': True, 'data': user_dict})
        return jsonify({'error': error or 'Invalid credentials'}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    try:
        AuditLog.log(current_user.id, 'logout', 'User logged out')
        logout_user()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/me', methods=['GET'])
@login_required
def me():
    try:
        user = User.get_by_id(current_user.id)
        if user:
            user_dict = dict(user)
            if 'password_hash' in user_dict:
                del user_dict['password_hash']
            return jsonify({'success': True, 'data': user_dict})
        return jsonify({'error': 'User not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/profile', methods=['PUT'])
@login_required
def profile():
    try:
        data = request.json or {}
        success = update_profile(current_user.id, data)
        if success:
            AuditLog.log(current_user.id, 'update_profile', 'User updated profile')
            return jsonify({'success': True})
        return jsonify({'error': 'Profile update failed'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/password', methods=['PUT'])
@login_required
def password():
    try:
        data = request.json or {}
        success, error = change_password(current_user.id, data.get('old_password'), data.get('new_password'))
        if success:
            AuditLog.log(current_user.id, 'change_password', 'User changed password')
            return jsonify({'success': True})
        return jsonify({'error': error or 'Password change failed'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/profile-photo', methods=['POST'])
@login_required
def profile_photo():
    try:
        file = request.files.get('photo') or request.files.get('file')
        if not file:
            return jsonify({'error': 'No file selected'}), 400
        from services.file_service import save_file
        doc_id, error = save_file(file, 'profile_photos', current_user.id)
        if doc_id:
            photo_url = f"/api/documents/{doc_id}"
            User.update(current_user.id, {'profile_photo': photo_url})
            AuditLog.log(current_user.id, 'update_photo', 'User updated profile photo')
            return jsonify({'success': True, 'photo_url': photo_url, 'data': {'document_id': doc_id, 'photo_url': photo_url}})
        return jsonify({'error': error or 'Failed to save file'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

