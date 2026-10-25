from models.db import get_db

class MedicalRecord:
    @staticmethod
    def get_all(user_id, filters=None, page=1, per_page=50):
        db = get_db()
        query = """
            SELECT mr.*, fm.name as member_name 
            FROM medical_records mr 
            LEFT JOIN family_members fm ON mr.family_member_id = fm.id 
            WHERE mr.user_id = ?
        """
        values = [user_id]
        
        if filters:
            if filters.get('family_member_id'):
                query += " AND mr.family_member_id = ?"
                values.append(filters['family_member_id'])
            if filters.get('record_type'):
                query += " AND LOWER(mr.record_type) = LOWER(?)"
                values.append(filters['record_type'])
                
        query += " ORDER BY mr.record_date DESC LIMIT ? OFFSET ?"
        values.extend([per_page, (page - 1) * per_page])
        
        return db.execute(query, values).fetchall()
        
    @staticmethod
    def get_by_id(record_id, user_id):
        db = get_db()
        return db.execute('SELECT * FROM medical_records WHERE id = ? AND user_id = ?', (record_id, user_id)).fetchone()
        
    @staticmethod
    def get_by_member(member_id, user_id):
        db = get_db()
        return db.execute('SELECT * FROM medical_records WHERE family_member_id = ? AND user_id = ? ORDER BY record_date DESC', (member_id, user_id)).fetchall()
        
    @staticmethod
    def create(user_id, data):
        db = get_db()
        data['user_id'] = user_id
        fields = ['user_id', 'family_member_id', 'title', 'record_type', 'record_date', 'doctor', 'hospital', 'description', 'diagnosis', 'notes', 'tags']
        
        insert_fields = []
        values = []
        placeholders = []
        
        for field in fields:
            if field in data:
                insert_fields.append(field)
                values.append(data[field])
                placeholders.append('?')
                
        query = f"INSERT INTO medical_records ({', '.join(insert_fields)}) VALUES ({', '.join(placeholders)})"
        cursor = db.execute(query, values)
        db.commit()
        return cursor.lastrowid
        
    @staticmethod
    def update(record_id, user_id, data):
        db = get_db()
        allowed = ['title', 'record_type', 'record_date', 'doctor', 'hospital', 'description', 'diagnosis', 'notes', 'tags']
        fields = []
        values = []
        
        for k, v in data.items():
            if k in allowed:
                fields.append(f"{k} = ?")
                values.append(v)
                
        if not fields:
            return False
            
        values.extend([record_id, user_id])
        query = f"UPDATE medical_records SET {', '.join(fields)}, updated_at = CURRENT_TIMESTAMP WHERE id = ? AND user_id = ?"
        cursor = db.execute(query, values)
        db.commit()
        return cursor.rowcount > 0
        
    @staticmethod
    def delete(record_id, user_id):
        db = get_db()
        cursor = db.execute('DELETE FROM medical_records WHERE id = ? AND user_id = ?', (record_id, user_id))
        db.commit()
        return cursor.rowcount > 0
        
    @staticmethod
    def get_recent(user_id, limit=5):
        db = get_db()
        return db.execute('SELECT * FROM medical_records WHERE user_id = ? ORDER BY record_date DESC LIMIT ?', (user_id, limit)).fetchall()
        
    @staticmethod
    def search(user_id, query):
        db = get_db()
        search_term = f"%{query}%"
        return db.execute('''
            SELECT * FROM medical_records 
            WHERE user_id = ? AND (title LIKE ? OR diagnosis LIKE ? OR notes LIKE ? OR tags LIKE ?)
            ORDER BY record_date DESC
        ''', (user_id, search_term, search_term, search_term, search_term)).fetchall()
