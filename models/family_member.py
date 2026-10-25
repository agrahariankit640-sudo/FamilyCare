from models.db import get_db

class FamilyMember:
    @staticmethod
    def get_all(user_id):
        db = get_db()
        return db.execute('SELECT * FROM family_members WHERE user_id = ? AND is_archived = 0 ORDER BY name', (user_id,)).fetchall()
        
    @staticmethod
    def get_by_id(member_id, user_id):
        db = get_db()
        return db.execute('SELECT * FROM family_members WHERE id = ? AND user_id = ?', (member_id, user_id)).fetchone()
        
    @staticmethod
    def create(user_id, data):
        db = get_db()
        fields = ['user_id', 'name', 'relationship', 'gender', 'date_of_birth', 'blood_group', 
                  'phone', 'email', 'address', 'emergency_contact', 'emergency_contact_phone', 
                  'allergies', 'existing_conditions', 'important_notes']
        
        insert_fields = []
        values = []
        placeholders = []
        
        data['user_id'] = user_id
        
        for field in fields:
            if field in data:
                insert_fields.append(field)
                values.append(data[field])
                placeholders.append('?')
                
        query = f"INSERT INTO family_members ({', '.join(insert_fields)}) VALUES ({', '.join(placeholders)})"
        cursor = db.execute(query, values)
        db.commit()
        return cursor.lastrowid
        
    @staticmethod
    def update(member_id, user_id, data):
        db = get_db()
        fields = []
        values = []
        allowed = ['name', 'relationship', 'gender', 'date_of_birth', 'blood_group', 
                   'phone', 'email', 'address', 'emergency_contact', 'emergency_contact_phone', 
                   'allergies', 'existing_conditions', 'important_notes', 'profile_photo']
                   
        for k, v in data.items():
            if k in allowed:
                fields.append(f"{k} = ?")
                values.append(v)
                
        if not fields:
            return False
            
        values.extend([member_id, user_id])
        query = f"UPDATE family_members SET {', '.join(fields)}, updated_at = CURRENT_TIMESTAMP WHERE id = ? AND user_id = ?"
        cursor = db.execute(query, values)
        db.commit()
        return cursor.rowcount > 0
        
    @staticmethod
    def archive(member_id, user_id):
        db = get_db()
        cursor = db.execute('UPDATE family_members SET is_archived = 1 WHERE id = ? AND user_id = ?', (member_id, user_id))
        db.commit()
        return cursor.rowcount > 0
        
    @staticmethod
    def delete(member_id, user_id):
        db = get_db()
        cursor = db.execute('DELETE FROM family_members WHERE id = ? AND user_id = ?', (member_id, user_id))
        db.commit()
        return cursor.rowcount > 0
        
    @staticmethod
    def get_count(user_id):
        db = get_db()
        result = db.execute('SELECT COUNT(*) as count FROM family_members WHERE user_id = ? AND is_archived = 0', (user_id,)).fetchone()
        return result['count'] if result else 0
