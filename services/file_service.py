import os
from werkzeug.utils import secure_filename
from flask import current_app
from models.document import Document
from utils.helpers import generate_filename, allowed_file
from utils.constants import MAX_FILE_SIZE

def save_file(file, category, user_id, family_member_id=None, record_id=None):
    if not file or not allowed_file(file.filename):
        return None, "Invalid file type"
        
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)
    
    if file_size > MAX_FILE_SIZE:
        return None, "File too large"

    original_filename = secure_filename(file.filename)
    stored_filename = generate_filename(original_filename)
    
    upload_folder = current_app.config['UPLOAD_FOLDER']
    user_folder = os.path.join(upload_folder, str(user_id))
    os.makedirs(user_folder, exist_ok=True)
    
    file_path = os.path.join(user_folder, stored_filename)
    file.save(file_path)
    
    file_type = original_filename.rsplit('.', 1)[1].lower() if '.' in original_filename else ''
    
    data = {
        'original_filename': original_filename,
        'stored_filename': stored_filename,
        'file_path': file_path,
        'file_type': file_type,
        'file_size': file_size,
        'category': category,
        'family_member_id': family_member_id,
        'medical_record_id': record_id
    }
    
    doc_id = Document.create(user_id, data)
    return doc_id, None

def delete_file(document_id, user_id):
    doc = Document.get_by_id(document_id, user_id)
    if not doc:
        return False
        
    try:
        if os.path.exists(doc['file_path']):
            os.remove(doc['file_path'])
    except Exception:
        pass # Log error in production
        
    return Document.delete(document_id, user_id)

def get_file_path(document_id, user_id):
    doc = Document.get_by_id(document_id, user_id)
    if not doc:
        return None
    return doc['file_path']

def validate_upload(file):
    if not file or not file.filename:
        return False, "No file selected"
    if not allowed_file(file.filename):
        return False, "File type not allowed"
    return True, None
