from models.db import get_db

class InsuranceClaim:
    @staticmethod
    def get_all(user_id, policy_id=None):
        db = get_db()
        query = """
            SELECT ic.*, ip.provider as policy_name, ip.policy_number, fm.name as member_name 
            FROM insurance_claims ic 
            LEFT JOIN insurance_policies ip ON ic.policy_id = ip.id 
            LEFT JOIN family_members fm ON ip.family_member_id = fm.id 
            WHERE ic.user_id = ?
        """
        values = [user_id]
        
        if policy_id:
            query += " AND ic.policy_id = ?"
            values.append(policy_id)
            
        query += " ORDER BY ic.claim_date DESC"
        return db.execute(query, values).fetchall()
        
    @staticmethod
    def get_by_id(claim_id, user_id):
        db = get_db()
        return db.execute('''
            SELECT ic.*, ip.provider as policy_name, ip.policy_number, fm.name as member_name 
            FROM insurance_claims ic 
            LEFT JOIN insurance_policies ip ON ic.policy_id = ip.id 
            LEFT JOIN family_members fm ON ip.family_member_id = fm.id 
            WHERE ic.id = ? AND ic.user_id = ?
        ''', (claim_id, user_id)).fetchone()
        
    @staticmethod
    def create(user_id, data):
        db = get_db()
        data = dict(data)
        data['user_id'] = user_id
        if 'hospital_name' in data and not data.get('hospital'):
            data['hospital'] = data['hospital_name']
            
        fields = ['policy_id', 'user_id', 'claim_number', 'claim_date', 'amount', 'hospital', 'status', 'description', 'document_id']
        
        insert_fields = []
        values = []
        placeholders = []
        
        for field in fields:
            if field in data and data[field] is not None and data[field] != '':
                insert_fields.append(field)
                values.append(data[field])
                placeholders.append('?')
                
        query = f"INSERT INTO insurance_claims ({', '.join(insert_fields)}) VALUES ({', '.join(placeholders)})"
        cursor = db.execute(query, values)
        db.commit()
        return cursor.lastrowid
        
    @staticmethod
    def update(claim_id, user_id, data):
        db = get_db()
        data = dict(data)
        if 'hospital_name' in data and not data.get('hospital'):
            data['hospital'] = data['hospital_name']
            
        allowed = ['policy_id', 'claim_number', 'claim_date', 'amount', 'hospital', 'status', 'description', 'document_id']
        fields = []
        values = []
        
        for k, v in data.items():
            if k in allowed:
                fields.append(f"{k} = ?")
                values.append(v)
                
        if not fields:
            return False
            
        values.extend([claim_id, user_id])
        query = f"UPDATE insurance_claims SET {', '.join(fields)}, updated_at = CURRENT_TIMESTAMP WHERE id = ? AND user_id = ?"
        db.execute(query, values)
        db.commit()
        return True
        
    @staticmethod
    def delete(claim_id, user_id):
        db = get_db()
        db.execute('DELETE FROM insurance_claims WHERE id = ? AND user_id = ?', (claim_id, user_id))
        db.commit()
        return True
