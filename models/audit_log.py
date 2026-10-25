from models.db import get_db
from flask import request

class AuditLog:
    @staticmethod
    def log(user_id, action, entity_type=None, entity_id=None, details=None, ip_address=None):
        db = get_db()
        if ip_address is None and request:
            ip_address = request.remote_addr
            
        cursor = db.execute(
            'INSERT INTO audit_logs (user_id, action, entity_type, entity_id, details, ip_address) VALUES (?, ?, ?, ?, ?, ?)',
            (user_id, action, entity_type, entity_id, details, ip_address)
        )
        db.commit()
        return cursor.lastrowid
        
    @staticmethod
    def get_all(user_id=None, limit=100):
        db = get_db()
        if user_id:
            return db.execute('SELECT * FROM audit_logs WHERE user_id = ? ORDER BY created_at DESC LIMIT ?', (user_id, limit)).fetchall()
        return db.execute('SELECT * FROM audit_logs ORDER BY created_at DESC LIMIT ?', (limit,)).fetchall()
        
    @staticmethod
    def get_by_user(user_id, limit=50):
        db = get_db()
        return db.execute('SELECT * FROM audit_logs WHERE user_id = ? ORDER BY created_at DESC LIMIT ?', (user_id, limit)).fetchall()
