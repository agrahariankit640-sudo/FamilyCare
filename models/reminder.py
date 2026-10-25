from models.db import get_db
from datetime import datetime

class Reminder:
    @staticmethod
    def get_all(user_id, status=None, date=None):
        db = get_db()
        query = """
            SELECT r.*, m.name as medicine_name, fm.name as member_name 
            FROM medicine_reminders r 
            JOIN medicines m ON r.medicine_id = m.id 
            LEFT JOIN family_members fm ON r.family_member_id = fm.id 
            WHERE r.user_id = ?
        """
        values = [user_id]
        
        if status:
            query += " AND LOWER(r.status) = LOWER(?)"
            values.append(status)
        if date:
            query += " AND r.reminder_date = ?"
            values.append(date)
            
        query += " ORDER BY r.reminder_date, r.reminder_time"
        return db.execute(query, values).fetchall()
        
    @staticmethod
    def get_by_id(reminder_id, user_id):
        db = get_db()
        return db.execute('SELECT * FROM medicine_reminders WHERE id = ? AND user_id = ?', (reminder_id, user_id)).fetchone()
        
    @staticmethod
    def create(user_id, data):
        db = get_db()
        data = dict(data)
        data['user_id'] = user_id
        if 'medicine_id' in data and not data.get('family_member_id'):
            med = db.execute('SELECT family_member_id FROM medicines WHERE id = ?', (data['medicine_id'],)).fetchone()
            if med and med['family_member_id']:
                data['family_member_id'] = med['family_member_id']
        if not data.get('reminder_date'):
            data['reminder_date'] = datetime.now().strftime('%Y-%m-%d')
        if not data.get('status'):
            data['status'] = 'pending'
            
        fields = ['medicine_id', 'family_member_id', 'user_id', 'reminder_date', 'reminder_time', 'frequency', 'status']
        
        insert_fields = []
        values = []
        placeholders = []
        
        for field in fields:
            if field in data and data[field] is not None and data[field] != '':
                insert_fields.append(field)
                values.append(data[field])
                placeholders.append('?')
                
        query = f"INSERT INTO medicine_reminders ({', '.join(insert_fields)}) VALUES ({', '.join(placeholders)})"
        cursor = db.execute(query, values)
        db.commit()
        return cursor.lastrowid
        
    @staticmethod
    def update_status(reminder_id, user_id, status):
        db = get_db()
        db.execute('UPDATE medicine_reminders SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ? AND user_id = ?', (status, reminder_id, user_id))
        db.commit()
        return True
        
    @staticmethod
    def delete(reminder_id, user_id):
        db = get_db()
        db.execute('DELETE FROM medicine_reminders WHERE id = ? AND user_id = ?', (reminder_id, user_id))
        db.commit()
        return True
        
    @staticmethod
    def get_pending(user_id):
        db = get_db()
        return db.execute("SELECT r.*, m.name as medicine_name FROM medicine_reminders r JOIN medicines m ON r.medicine_id = m.id WHERE r.user_id = ? AND r.status = 'pending' ORDER BY r.reminder_date, r.reminder_time", (user_id,)).fetchall()
        
    @staticmethod
    def get_today(user_id):
        today = datetime.now().strftime('%Y-%m-%d')
        db = get_db()
        return db.execute("SELECT r.*, m.name as medicine_name FROM medicine_reminders r JOIN medicines m ON r.medicine_id = m.id WHERE r.user_id = ? AND r.reminder_date = ? ORDER BY r.reminder_time", (user_id, today)).fetchall()
