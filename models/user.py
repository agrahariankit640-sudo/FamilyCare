from models.db import get_db
from flask_login import UserMixin

class UserLogin(UserMixin):
    def __init__(self, user_dict):
        self.id = user_dict['id']
        self.name = user_dict['name']
        self.email = user_dict['email']
        self.role = user_dict['role']
        self.profile_photo = user_dict['profile_photo'] if 'profile_photo' in user_dict.keys() else None
        self.currency = user_dict['currency'] if 'currency' in user_dict.keys() else 'USD'
        self._is_active = bool(user_dict['is_active']) if 'is_active' in user_dict.keys() else True
        
    @property
    def is_active(self):
        return self._is_active

    def get_id(self):
        return str(self.id)

class User:
    @staticmethod
    def get_by_id(user_id):
        db = get_db()
        return db.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
        
    @staticmethod
    def get_by_email(email):
        db = get_db()
        return db.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        
    @staticmethod
    def create(name, email, phone, password_hash, role='user'):
        db = get_db()
        cursor = db.execute(
            'INSERT INTO users (name, email, phone, password_hash, role) VALUES (?, ?, ?, ?, ?)',
            (name, email, phone, password_hash, role)
        )
        db.commit()
        return cursor.lastrowid
        
    @staticmethod
    def update(user_id, data):
        db = get_db()
        fields = []
        values = []
        for k, v in data.items():
            if k in ['name', 'phone', 'currency', 'profile_photo']:
                fields.append(f"{k} = ?")
                values.append(v)
        if not fields:
            return False
            
        values.append(user_id)
        query = f"UPDATE users SET {', '.join(fields)}, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
        db.execute(query, values)
        db.commit()
        return True
        
    @staticmethod
    def update_password(user_id, password_hash):
        db = get_db()
        db.execute('UPDATE users SET password_hash = ? WHERE id = ?', (password_hash, user_id))
        db.commit()
        return True
        
    @staticmethod
    def update_photo(user_id, photo_path):
        db = get_db()
        db.execute('UPDATE users SET profile_photo = ? WHERE id = ?', (photo_path, user_id))
        db.commit()
        return True
        
    @staticmethod
    def get_all():
        db = get_db()
        return db.execute('SELECT id, name, email, phone, role, is_active, created_at FROM users ORDER BY created_at DESC').fetchall()
        
    @staticmethod
    def set_active(user_id, is_active):
        db = get_db()
        db.execute('UPDATE users SET is_active = ? WHERE id = ?', (int(is_active), user_id))
        db.commit()
        return True
        
    @staticmethod
    def delete(user_id):
        db = get_db()
        db.execute('DELETE FROM users WHERE id = ?', (user_id,))
        db.commit()
        return True
