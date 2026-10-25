from models.db import get_db

class Appointment:
    @staticmethod
    def get_all(user_id, member_id=None, status=None):
        db = get_db()
        query = """
            SELECT dv.*, fm.name as member_name 
            FROM doctor_visits dv 
            LEFT JOIN family_members fm ON dv.family_member_id = fm.id 
            WHERE dv.user_id = ?
        """
        values = [user_id]
        
        if member_id:
            query += " AND dv.family_member_id = ?"
            values.append(member_id)
        if status:
            query += " AND LOWER(dv.status) = LOWER(?)"
            values.append(status)
            
        query += " ORDER BY dv.visit_date DESC"
        return db.execute(query, values).fetchall()
        
    @staticmethod
    def get_by_id(appt_id, user_id):
        db = get_db()
        return db.execute('SELECT * FROM doctor_visits WHERE id = ? AND user_id = ?', (appt_id, user_id)).fetchone()
        
    @staticmethod
    def create(user_id, data):
        db = get_db()
        data['user_id'] = user_id
        fields = ['family_member_id', 'user_id', 'doctor_name', 'hospital', 'specialization', 'visit_date', 'visit_time', 'reason', 'notes', 'follow_up_date', 'status']
        
        insert_fields = []
        values = []
        placeholders = []
        
        for field in fields:
            if field in data:
                insert_fields.append(field)
                values.append(data[field])
                placeholders.append('?')
                
        query = f"INSERT INTO doctor_visits ({', '.join(insert_fields)}) VALUES ({', '.join(placeholders)})"
        cursor = db.execute(query, values)
        db.commit()
        return cursor.lastrowid
        
    @staticmethod
    def update(appt_id, user_id, data):
        db = get_db()
        allowed = ['doctor_name', 'hospital', 'specialization', 'visit_date', 'visit_time', 'reason', 'notes', 'follow_up_date', 'status']
        fields = []
        values = []
        
        for k, v in data.items():
            if k in allowed:
                fields.append(f"{k} = ?")
                values.append(v)
                
        if not fields:
            return False
            
        values.extend([appt_id, user_id])
        query = f"UPDATE doctor_visits SET {', '.join(fields)}, updated_at = CURRENT_TIMESTAMP WHERE id = ? AND user_id = ?"
        cursor = db.execute(query, values)
        db.commit()
        return cursor.rowcount > 0
        
    @staticmethod
    def delete(appt_id, user_id):
        db = get_db()
        cursor = db.execute('DELETE FROM doctor_visits WHERE id = ? AND user_id = ?', (appt_id, user_id))
        db.commit()
        return cursor.rowcount > 0
        
    @staticmethod
    def get_upcoming(user_id, limit=5):
        db = get_db()
        return db.execute("SELECT * FROM doctor_visits WHERE user_id = ? AND status = 'upcoming' ORDER BY visit_date ASC LIMIT ?", (user_id, limit)).fetchall()
        
    @staticmethod
    def get_upcoming_count(user_id):
        db = get_db()
        result = db.execute("SELECT COUNT(*) as count FROM doctor_visits WHERE user_id = ? AND status = 'upcoming'", (user_id,)).fetchone()
        return result['count'] if result else 0
