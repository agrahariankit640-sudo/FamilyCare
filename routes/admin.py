from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from models.user import User
from models.audit_log import AuditLog

admin_bp = Blueprint('admin', __name__)

def check_admin():
    if not current_user.is_authenticated or getattr(current_user, 'role', '') != 'admin':
        raise Exception('Unauthorized: Admin access required')

@admin_bp.route('/stats', methods=['GET'])
@login_required
def stats():
    try:
        check_admin()
        from models.db import get_db
        db = get_db()
        users_count = db.execute('SELECT COUNT(*) as c FROM users').fetchone()['c']
        profiles_count = db.execute('SELECT COUNT(*) as c FROM family_members').fetchone()['c']
        records_count = db.execute('SELECT COUNT(*) as c FROM medical_records').fetchone()['c']
        docs_count = db.execute('SELECT COUNT(*) as c FROM medical_documents').fetchone()['c']
        return jsonify({
            'success': True,
            'data': {
                'users': users_count,
                'totalUsers': users_count,
                'profiles': profiles_count,
                'records': records_count,
                'docs': docs_count
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 403

@admin_bp.route('/users', methods=['GET'])
@login_required
def get_users():
    try:
        check_admin()
        users = User.get_all()
        return jsonify({'success': True, 'data': [dict(u) for u in users]})
    except Exception as e:
        return jsonify({'error': str(e)}), 403

@admin_bp.route('/users/<int:id>/status', methods=['PUT'])
@login_required
def update_user_status(id):
    try:
        check_admin()
        data = request.json or {}
        is_active = data.get('is_active')
        if is_active is None and 'status' in data:
            status_val = str(data['status']).lower()
            is_active = status_val in ['active', '1', 'true']
        else:
            is_active = bool(is_active)
        User.set_active(id, 1 if is_active else 0)
        AuditLog.log(current_user.id, 'update_user_status', 'users', id, f'Set active={is_active}')
        return jsonify({'success': True, 'message': 'User status updated successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 403

@admin_bp.route('/activity-log', methods=['GET'])
@login_required
def activity_log():
    try:
        check_admin()
        action = request.args.get('action')
        from models.db import get_db
        db = get_db()
        if action:
            logs = db.execute('''
                SELECT * FROM audit_logs 
                WHERE action LIKE ? 
                ORDER BY created_at DESC LIMIT 100
            ''', (f'%{action}%',)).fetchall()
        else:
            logs = AuditLog.get_all(limit=100)
        return jsonify({'success': True, 'data': [dict(l) for l in logs]})
    except Exception as e:
        return jsonify({'error': str(e)}), 403

