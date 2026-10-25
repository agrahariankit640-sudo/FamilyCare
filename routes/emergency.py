from flask import Blueprint, jsonify
from flask_login import login_required, current_user
from models.family_member import FamilyMember

emergency_bp = Blueprint('emergency', __name__)

@emergency_bp.route('/<int:member_id>', methods=['GET'])
@login_required
def emergency_member(member_id):
    try:
        member = FamilyMember.get_by_id(member_id, current_user.id)
        if member:
            return jsonify({'success': True, 'data': member})
        return jsonify({'error': 'Not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@emergency_bp.route('/all', methods=['GET'])
@login_required
def emergency_all():
    try:
        members = FamilyMember.get_all(current_user.id)
        return jsonify({'success': True, 'data': members})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
