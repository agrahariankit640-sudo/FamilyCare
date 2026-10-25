from models.db import get_db

class Medicine:
    @staticmethod
    def get_all(user_id, member_id=None, status=None):
        db = get_db()
        query = """
            SELECT m.*, fm.name as member_name 
            FROM medicines m 
            LEFT JOIN family_members fm ON m.family_member_id = fm.id 
            WHERE m.user_id = ?
        """
        values = [user_id]
        
        if member_id:
            query += " AND m.family_member_id = ?"
            values.append(member_id)
        if status:
            query += " AND LOWER(m.status) = LOWER(?)"
            values.append(status)
            
        query += " ORDER BY m.start_date DESC"
        return db.execute(query, values).fetchall()
        
    @staticmethod
    def get_by_id(med_id, user_id):
        db = get_db()
        return db.execute('SELECT * FROM medicines WHERE id = ? AND user_id = ?', (med_id, user_id)).fetchone()
        
    @staticmethod
    def create(user_id, data):
        db = get_db()
        data['user_id'] = user_id
        fields = ['family_member_id', 'user_id', 'name', 'dosage', 'frequency', 'start_date', 'end_date', 'time_of_day', 'instructions', 'doctor', 'notes', 'status']
        
        insert_fields = []
        values = []
        placeholders = []
        
        for field in fields:
            if field in data:
                insert_fields.append(field)
                values.append(data[field])
                placeholders.append('?')
                
        query = f"INSERT INTO medicines ({', '.join(insert_fields)}) VALUES ({', '.join(placeholders)})"
        cursor = db.execute(query, values)
        db.commit()
        return cursor.lastrowid
        
    @staticmethod
    def update(med_id, user_id, data):
        db = get_db()
        allowed = ['name', 'dosage', 'frequency', 'start_date', 'end_date', 'time_of_day', 'instructions', 'doctor', 'notes', 'status']
        fields = []
        values = []
        
        for k, v in data.items():
            if k in allowed:
                fields.append(f"{k} = ?")
                values.append(v)
                
        if not fields:
            return False
            
        values.extend([med_id, user_id])
        query = f"UPDATE medicines SET {', '.join(fields)}, updated_at = CURRENT_TIMESTAMP WHERE id = ? AND user_id = ?"
        cursor = db.execute(query, values)
        db.commit()
        return cursor.rowcount > 0
        
    @staticmethod
    def update_status(med_id, user_id, status):
        db = get_db()
        cursor = db.execute('UPDATE medicines SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ? AND user_id = ?', (status, med_id, user_id))
        db.commit()
        return cursor.rowcount > 0
        
    @staticmethod
    def delete(med_id, user_id):
        db = get_db()
        cursor = db.execute('DELETE FROM medicines WHERE id = ? AND user_id = ?', (med_id, user_id))
        db.commit()
        return cursor.rowcount > 0
        
    @staticmethod
    def get_active(user_id):
        db = get_db()
        return db.execute("SELECT * FROM medicines WHERE user_id = ? AND status = 'active' ORDER BY name", (user_id,)).fetchall()
        
    @staticmethod
    def get_active_count(user_id):
        db = get_db()
        result = db.execute("SELECT COUNT(*) as count FROM medicines WHERE user_id = ? AND status = 'active'", (user_id,)).fetchone()
        return result['count'] if result else 0
