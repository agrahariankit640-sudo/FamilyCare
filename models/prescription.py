from models.db import get_db

class Prescription:
    @staticmethod
    def get_all(user_id, member_id=None):
        db = get_db()
        if member_id:
            return db.execute('''
                SELECT p.*, fm.name as member_name 
                FROM prescriptions p 
                LEFT JOIN family_members fm ON p.family_member_id = fm.id 
                WHERE p.user_id = ? AND p.family_member_id = ? 
                ORDER BY p.prescription_date DESC
            ''', (user_id, member_id)).fetchall()
        return db.execute('''
            SELECT p.*, fm.name as member_name 
            FROM prescriptions p 
            LEFT JOIN family_members fm ON p.family_member_id = fm.id 
            WHERE p.user_id = ? 
            ORDER BY p.prescription_date DESC
        ''', (user_id,)).fetchall()
        
    @staticmethod
    def get_by_id(rx_id, user_id):
        db = get_db()
        return db.execute('''
            SELECT p.*, fm.name as member_name 
            FROM prescriptions p 
            LEFT JOIN family_members fm ON p.family_member_id = fm.id 
            WHERE p.id = ? AND p.user_id = ?
        ''', (rx_id, user_id)).fetchone()
        
    @staticmethod
    def create(user_id, data):
        db = get_db()
        data['user_id'] = user_id
        fields = ['family_member_id', 'user_id', 'medicine_name', 'doctor', 'prescription_date', 'dosage', 'frequency', 'duration', 'instructions', 'notes', 'document_id']
        
        insert_fields = []
        values = []
        placeholders = []
        
        for field in fields:
            if field in data:
                insert_fields.append(field)
                values.append(data[field])
                placeholders.append('?')
                
        query = f"INSERT INTO prescriptions ({', '.join(insert_fields)}) VALUES ({', '.join(placeholders)})"
        cursor = db.execute(query, values)
        db.commit()
        return cursor.lastrowid
        
    @staticmethod
    def update(rx_id, user_id, data):
        db = get_db()
        allowed = ['medicine_name', 'doctor', 'prescription_date', 'dosage', 'frequency', 'duration', 'instructions', 'notes']
        fields = []
        values = []
        
        for k, v in data.items():
            if k in allowed:
                fields.append(f"{k} = ?")
                values.append(v)
                
        if not fields:
            return False
            
        values.extend([rx_id, user_id])
        query = f"UPDATE prescriptions SET {', '.join(fields)} WHERE id = ? AND user_id = ?"
        db.execute(query, values)
        db.commit()
        return True
        
    @staticmethod
    def delete(rx_id, user_id):
        db = get_db()
        db.execute('DELETE FROM prescriptions WHERE id = ? AND user_id = ?', (rx_id, user_id))
        db.commit()
        return True
