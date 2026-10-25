from models.db import get_db

class TestRecord:
    @staticmethod
    def get_all(user_id, member_id=None):
        db = get_db()
        query = """
            SELECT t.*, fm.name as member_name 
            FROM tests t 
            LEFT JOIN family_members fm ON t.family_member_id = fm.id 
            WHERE t.user_id = ?
        """
        values = [user_id]
        
        if member_id:
            query += " AND t.family_member_id = ?"
            values.append(member_id)
            
        query += " ORDER BY t.test_date DESC"
        return db.execute(query, values).fetchall()
        
    @staticmethod
    def get_by_id(test_id, user_id):
        db = get_db()
        return db.execute('''
            SELECT t.*, fm.name as member_name 
            FROM tests t 
            LEFT JOIN family_members fm ON t.family_member_id = fm.id 
            WHERE t.id = ? AND t.user_id = ?
        ''', (test_id, user_id)).fetchone()
        
    @staticmethod
    def create(user_id, data):
        db = get_db()
        data = dict(data)
        data['user_id'] = user_id
        if 'member_id' in data and not data.get('family_member_id'):
            data['family_member_id'] = data['member_id']
        if 'doctor_name' in data and not data.get('doctor'):
            data['doctor'] = data['doctor_name']
        if 'followup_date' in data and not data.get('follow_up_date'):
            data['follow_up_date'] = data['followup_date']
            
        fields = ['family_member_id', 'user_id', 'test_name', 'test_date', 'doctor', 'result_summary', 'document_id', 'follow_up_date', 'notes']
        
        insert_fields = []
        values = []
        placeholders = []
        
        for field in fields:
            if field in data and data[field] is not None and data[field] != '':
                insert_fields.append(field)
                values.append(data[field])
                placeholders.append('?')
                
        query = f"INSERT INTO tests ({', '.join(insert_fields)}) VALUES ({', '.join(placeholders)})"
        cursor = db.execute(query, values)
        db.commit()
        return cursor.lastrowid
        
    @staticmethod
    def update(test_id, user_id, data):
        db = get_db()
        data = dict(data)
        if 'member_id' in data and not data.get('family_member_id'):
            data['family_member_id'] = data['member_id']
        if 'doctor_name' in data and not data.get('doctor'):
            data['doctor'] = data['doctor_name']
        if 'followup_date' in data and not data.get('follow_up_date'):
            data['follow_up_date'] = data['followup_date']
            
        allowed = ['family_member_id', 'test_name', 'test_date', 'doctor', 'result_summary', 'document_id', 'follow_up_date', 'notes']
        fields = []
        values = []
        
        for k, v in data.items():
            if k in allowed:
                fields.append(f"{k} = ?")
                values.append(v)
                
        if not fields:
            return False
            
        values.extend([test_id, user_id])
        query = f"UPDATE tests SET {', '.join(fields)} WHERE id = ? AND user_id = ?"
        db.execute(query, values)
        db.commit()
        return True
        
    @staticmethod
    def delete(test_id, user_id):
        db = get_db()
        db.execute('DELETE FROM tests WHERE id = ? AND user_id = ?', (test_id, user_id))
        db.commit()
        return True
        
    @staticmethod
    def get_pending_followups(user_id):
        db = get_db()
        return db.execute("""
            SELECT t.*, fm.name as member_name 
            FROM tests t 
            LEFT JOIN family_members fm ON t.family_member_id = fm.id 
            WHERE t.user_id = ? AND t.follow_up_date IS NOT NULL AND t.follow_up_date >= date('now') 
            ORDER BY t.follow_up_date ASC
        """, (user_id,)).fetchall()
