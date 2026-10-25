import os
from flask import Blueprint, request, jsonify, send_file
from flask_login import login_required, current_user
from models.document import Document
from models.audit_log import AuditLog
from services.file_service import save_file, delete_file, get_file_path

documents_bp = Blueprint('documents', __name__)

@documents_bp.route('/upload', methods=['POST'])
@login_required
def upload():
    try:
        file = request.files.get('document') or request.files.get('file')
        if not file or not file.filename:
            return jsonify({'error': 'No file part or file unselected'}), 400
        
        data = request.form.to_dict()
        category = data.get('category', 'documents')
        family_member_id = data.get('family_member_id') or data.get('member_id')
        record_id = data.get('medical_record_id') or data.get('record_id')
        
        doc_id, err = save_file(file, category, current_user.id, family_member_id, record_id)
        if err:
            return jsonify({'error': err}), 400
        if doc_id:
            AuditLog.log(current_user.id, 'upload_document', 'documents', doc_id, f'Uploaded document {doc_id}')
            return jsonify({'success': True, 'data': {'id': doc_id}})
        return jsonify({'error': 'Upload failed'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@documents_bp.route('/<int:id>', methods=['GET'])
@login_required
def get(id):
    try:
        doc = Document.get_by_id(id, current_user.id)
        if not doc:
            return jsonify({'error': 'Not found'}), 404
        file_path = doc['file_path']
        if file_path and os.path.exists(file_path):
            return send_file(file_path, download_name=doc['original_filename'])
        return jsonify({'error': 'File not found on disk'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@documents_bp.route('/<int:id>', methods=['DELETE'])
@login_required
def delete(id):
    try:
        doc = Document.get_by_id(id, current_user.id)
        if not doc:
            return jsonify({'error': 'Document not found'}), 404
        success = delete_file(id, current_user.id)
        if success:
            AuditLog.log(current_user.id, 'delete_document', 'documents', id, f'Deleted document {id}')
            return jsonify({'success': True})
        return jsonify({'error': 'Deletion failed'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

