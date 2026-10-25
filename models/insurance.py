from models.db import get_db

class InsurancePolicy:
    @staticmethod
    def get_all_policies(user_id):
        db = get_db()
        return db.execute('''
            SELECT ip.*, fm.name as member_name 
            FROM insurance_policies ip 
            LEFT JOIN family_members fm ON ip.family_member_id = fm.id 
            WHERE ip.user_id = ? 
            ORDER BY ip.expiry_date ASC
        ''', (user_id,)).fetchall()
        
    @staticmethod
    def get_policy_by_id(policy_id, user_id):
        db = get_db()
        return db.execute('''
            SELECT ip.*, fm.name as member_name 
            FROM insurance_policies ip 
            LEFT JOIN family_members fm ON ip.family_member_id = fm.id 
            WHERE ip.id = ? AND ip.user_id = ?
        ''', (policy_id, user_id)).fetchone()
        
    @staticmethod
    def create_policy(user_id, data):
        db = get_db()
        data = dict(data)
        data['user_id'] = user_id
        if 'provider_name' in data and not data.get('provider'):
            data['provider'] = data['provider_name']
        if 'member_id' in data and not data.get('family_member_id'):
            data['family_member_id'] = data['member_id']
        if 'valid_from' in data and not data.get('start_date'):
            data['start_date'] = data['valid_from']
        if 'valid_till' in data and not data.get('expiry_date'):
            data['expiry_date'] = data['valid_till']
        if 'premium_amount' in data and not data.get('premium'):
            data['premium'] = data['premium_amount']
            
        fields = ['family_member_id', 'user_id', 'provider', 'policy_number', 'policy_holder', 'start_date', 'expiry_date', 'coverage_amount', 'premium', 'contact_info', 'document_id', 'notes']
        
        insert_fields = []
        values = []
        placeholders = []
        
        for field in fields:
            if field in data and data[field] is not None and data[field] != '':
                insert_fields.append(field)
                values.append(data[field])
                placeholders.append('?')
                
        query = f"INSERT INTO insurance_policies ({', '.join(insert_fields)}) VALUES ({', '.join(placeholders)})"
        cursor = db.execute(query, values)
        db.commit()
        return cursor.lastrowid
        
    @staticmethod
    def update_policy(policy_id, user_id, data):
        db = get_db()
        data = dict(data)
        if 'provider_name' in data and not data.get('provider'):
            data['provider'] = data['provider_name']
        if 'member_id' in data and not data.get('family_member_id'):
            data['family_member_id'] = data['member_id']
        if 'valid_from' in data and not data.get('start_date'):
            data['start_date'] = data['valid_from']
        if 'valid_till' in data and not data.get('expiry_date'):
            data['expiry_date'] = data['valid_till']
        if 'premium_amount' in data and not data.get('premium'):
            data['premium'] = data['premium_amount']
            
        allowed = ['family_member_id', 'provider', 'policy_number', 'policy_holder', 'start_date', 'expiry_date', 'coverage_amount', 'premium', 'contact_info', 'document_id', 'notes']
        fields = []
        values = []
        
        for k, v in data.items():
            if k in allowed:
                fields.append(f"{k} = ?")
                values.append(v)
                
        if not fields:
            return False
            
        values.extend([policy_id, user_id])
        query = f"UPDATE insurance_policies SET {', '.join(fields)}, updated_at = CURRENT_TIMESTAMP WHERE id = ? AND user_id = ?"
        db.execute(query, values)
        db.commit()
        return True
        
    @staticmethod
    def delete_policy(policy_id, user_id):
        db = get_db()
        db.execute('DELETE FROM insurance_policies WHERE id = ? AND user_id = ?', (policy_id, user_id))
        db.commit()
        return True
        
    @staticmethod
    def get_expiring(user_id, days=30):
        db = get_db()
        return db.execute('''
            SELECT * FROM insurance_policies 
            WHERE user_id = ? AND expiry_date IS NOT NULL 
            AND expiry_date BETWEEN date('now') AND date('now', ?)
            ORDER BY expiry_date ASC
        ''', (user_id, f'+{days} days')).fetchall()
