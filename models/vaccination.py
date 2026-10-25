from models.db import get_db

class Vaccination:
    @staticmethod
    def get_all(user_id, member_id=None):
        db = get_db()
        query = """
            SELECT v.*, fm.name as member_name 
            FROM vaccinations v 
            LEFT JOIN family_members fm ON v.family_member_id = fm.id 
            WHERE v.user_id = ?
        """
        values = [user_id]
        
        if member_id:
            query += " AND v.family_member_id = ?"
            values.append(member_id)
            
        query += " ORDER BY v.vaccination_date DESC"
        return db.execute(query, values).fetchall()
        
    @staticmethod
    def get_by_id(vax_id, user_id):
        db = get_db()
        return db.execute('''
            SELECT v.*, fm.name as member_name 
            FROM vaccinations v 
            LEFT JOIN family_members fm ON v.family_member_id = fm.id 
            WHERE v.id = ? AND v.user_id = ?
        ''', (vax_id, user_id)).fetchone()
        
    @staticmethod
    def create(user_id, data):
        db = get_db()
        data = dict(data)
        data['user_id'] = user_id
        if 'member_id' in data and not data.get('family_member_id'):
            data['family_member_id'] = data['member_id']
        if 'date_administered' in data and not data.get('vaccination_date'):
            data['vaccination_date'] = data['date_administered']
        if 'hospital_name' in data and not data.get('hospital'):
            data['hospital'] = data['hospital_name']
        if 'next_due_date' in data and not data.get('next_dose_date'):
            data['next_dose_date'] = data['next_due_date']
            
        fields = ['family_member_id', 'user_id', 'vaccine_name', 'vaccination_date', 'dose_number', 'next_dose_date', 'hospital', 'notes', 'document_id']
        
        insert_fields = []
        values = []
        placeholders = []
        
        for field in fields:
            if field in data and data[field] is not None and data[field] != '':
                insert_fields.append(field)
                values.append(data[field])
                placeholders.append('?')
                
        query = f"INSERT INTO vaccinations ({', '.join(insert_fields)}) VALUES ({', '.join(placeholders)})"
        cursor = db.execute(query, values)
        db.commit()
        return cursor.lastrowid
        
    @staticmethod
    def update(vax_id, user_id, data):
        db = get_db()
        data = dict(data)
        if 'member_id' in data and not data.get('family_member_id'):
            data['family_member_id'] = data['member_id']
        if 'date_administered' in data and not data.get('vaccination_date'):
            data['vaccination_date'] = data['date_administered']
        if 'hospital_name' in data and not data.get('hospital'):
            data['hospital'] = data['hospital_name']
        if 'next_due_date' in data and not data.get('next_dose_date'):
            data['next_dose_date'] = data['next_due_date']
            
        allowed = ['family_member_id', 'vaccine_name', 'vaccination_date', 'dose_number', 'next_dose_date', 'hospital', 'notes', 'document_id']
        fields = []
        values = []
        
        for k, v in data.items():
            if k in allowed:
                fields.append(f"{k} = ?")
                values.append(v)
                
        if not fields:
            return False
            
        values.extend([vax_id, user_id])
        query = f"UPDATE vaccinations SET {', '.join(fields)} WHERE id = ? AND user_id = ?"
        db.execute(query, values)
        db.commit()
        return True
        
    @staticmethod
    def delete(vax_id, user_id):
        db = get_db()
        db.execute('DELETE FROM vaccinations WHERE id = ? AND user_id = ?', (vax_id, user_id))
        db.commit()
        return True
        
    @staticmethod
    def get_upcoming(user_id):
        db = get_db()
        return db.execute("""
            SELECT v.*, fm.name as member_name 
            FROM vaccinations v 
            LEFT JOIN family_members fm ON v.family_member_id = fm.id 
            WHERE v.user_id = ? AND v.next_dose_date IS NOT NULL AND v.next_dose_date >= date('now') 
            ORDER BY v.next_dose_date ASC
        """, (user_id,)).fetchall()
