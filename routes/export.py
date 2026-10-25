import io
import json
from flask import Blueprint, jsonify, send_file, Response
from flask_login import login_required, current_user
from services.export_service import export_backup_json, export_csv, export_family_summary
from models.audit_log import AuditLog

export_bp = Blueprint('export', __name__)

@export_bp.route('/backup', methods=['GET'])
@login_required
def backup():
    try:
        AuditLog.log(current_user.id, 'export_backup', 'system', current_user.id, 'Exported full JSON backup')
        json_str = export_backup_json(current_user.id)
        buf = io.BytesIO(json_str.encode('utf-8'))
        return send_file(
            buf,
            mimetype='application/json',
            as_attachment=True,
            download_name='familycare_backup.json'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@export_bp.route('/csv/<module>', methods=['GET'])
@login_required
def csv_export(module):
    try:
        AuditLog.log(current_user.id, 'export_csv', module, None, f'Exported CSV for {module}')
        csv_str = export_csv(current_user.id, module)
        if csv_str is None:
            return jsonify({'error': f'Unsupported module: {module}'}), 400
        buf = io.BytesIO(csv_str.encode('utf-8'))
        return send_file(
            buf,
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'familycare_{module}.csv'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@export_bp.route('/family-summary/<int:member_id>', methods=['GET'])
@login_required
def family_summary(member_id):
    try:
        AuditLog.log(current_user.id, 'export_summary', 'family_members', member_id, f'Exported summary for member {member_id}')
        summary = export_family_summary(current_user.id, member_id)
        if not summary:
            return jsonify({'error': 'Member not found'}), 404
        summary_json = json.dumps(summary, indent=2, default=str)
        buf = io.BytesIO(summary_json.encode('utf-8'))
        return send_file(
            buf,
            mimetype='application/json',
            as_attachment=True,
            download_name=f'family_summary_{member_id}.json'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

