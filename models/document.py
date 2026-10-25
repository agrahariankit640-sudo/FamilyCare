from models.db import get_db

class Document:
    @staticmethod
    def get_by_id(doc_id, user_id):
        db = get_db()
        return db.execute('SELECT * FROM medical_documents WHERE id = ? AND user_id = ?', (doc_id, user_id)).fetchone()
        
    @staticmethod
    def create(user_id, data):
        db = get_db()
        data['user_id'] = user_id
        fields = ['user_id', 'medical_record_id', 'family_member_id', 'original_filename', 'stored_filename', 'file_path', 'file_type', 'file_size', 'category']
        
        insert_fields = []
        values = []
        placeholders = []
        
        for field in fields:
            if field in data:
                insert_fields.append(field)
                values.append(data[field])
                placeholders.append('?')
                
        query = f"INSERT INTO medical_documents ({', '.join(insert_fields)}) VALUES ({', '.join(placeholders)})"
        cursor = db.execute(query, values)
        db.commit()
        return cursor.lastrowid
        
    @staticmethod
    def delete(doc_id, user_id):
        db = get_db()
        db.execute('DELETE FROM medical_documents WHERE id = ? AND user_id = ?', (doc_id, user_id))
        db.commit()
        return True
        
    @staticmethod
    def get_by_record(record_id, user_id):
        db = get_db()
        return db.execute('SELECT * FROM medical_documents WHERE medical_record_id = ? AND user_id = ?', (record_id, user_id)).fetchall()
        
    @staticmethod
    def get_by_member(member_id, user_id):
        db = get_db()
        return db.execute('SELECT * FROM medical_documents WHERE family_member_id = ? AND user_id = ?', (member_id, user_id)).fetchall()
