from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from models.health_parameter import HealthParameter
from models.audit_log import AuditLog

health_params_bp = Blueprint('health_params', __name__)

@health_params_bp.route('/', methods=['GET'])
@login_required
def get_all():
    try:
        member_id = request.args.get('family_member_id') or request.args.get('member_id') or request.args.get('memberId')
        parameter = request.args.get('parameter') or request.args.get('parameter_name') or request.args.get('type')
        items = HealthParameter.get_all(current_user.id, member_id=member_id, parameter=parameter)
        return jsonify({'success': True, 'data': items})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@health_params_bp.route('/', methods=['POST'])
@login_required
def create():
    try:
        data = request.json
        item_id = HealthParameter.create(current_user.id, data)
        if item_id:
            AuditLog.log(current_user.id, 'create_health_param', f'Created HealthParameter {item_id}')
            return jsonify({'success': True, 'data': {'id': item_id}})
        return jsonify({'error': 'Creation failed'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@health_params_bp.route('/<int:id>', methods=['DELETE'])
@login_required
def delete(id):
    try:
        success = HealthParameter.delete(id, current_user.id)
        if success:
            AuditLog.log(current_user.id, 'delete_health_param', f'Deleted HealthParameter {id}')
            return jsonify({'success': True})
        return jsonify({'error': 'Deletion failed'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@health_params_bp.route('/trends', methods=['GET'])
@login_required
def trends():
    try:
        member_id = request.args.get('family_member_id') or request.args.get('member_id') or request.args.get('memberId')
        parameter = request.args.get('parameter') or request.args.get('parameter_name') or request.args.get('type')
        days = request.args.get('days') or 90
        data = HealthParameter.get_trends(current_user.id, member_id, parameter, days)
        return jsonify({'success': True, 'data': data})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
