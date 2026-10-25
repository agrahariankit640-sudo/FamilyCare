import os
import tempfile
import shutil
import pytest
from app import create_app
from models.db import init_db

@pytest.fixture
def app():
    db_fd, db_path = tempfile.mkstemp(suffix='.db')
    upload_dir = tempfile.mkdtemp()
    
    test_app = create_app()
    test_app.config.update({
        'TESTING': True,
        'DATABASE_PATH': db_path,
        'UPLOAD_FOLDER': upload_dir,
        'WTF_CSRF_ENABLED': False
    })
    
    with test_app.app_context():
        init_db()
        
    yield test_app
    
    try:
        os.close(db_fd)
        if os.path.exists(db_path):
            os.unlink(db_path)
    except Exception:
        pass
    shutil.rmtree(upload_dir, ignore_errors=True)

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def registered_user(client):
    client.post('/api/auth/register', json={
        'name': 'Test User',
        'email': 'tester@example.com',
        'password': 'Password@123',
        'phone': '9876543210'
    })
    return {'email': 'tester@example.com', 'password': 'Password@123', 'name': 'Test User'}

@pytest.fixture
def auth_client(client, registered_user):
    client.post('/api/auth/login', json={
        'email': registered_user['email'],
        'password': registered_user['password']
    })
    return client

@pytest.fixture
def test_member(auth_client):
    res = auth_client.post('/api/family-members/', json={
        'name': 'Arun Sharma',
        'relationship': 'Brother',
        'gender': 'Male',
        'date_of_birth': '1990-05-15',
        'blood_group': 'O+',
        'allergies': 'Peanuts',
        'existing_conditions': 'None'
    })
    data = res.get_json()
    return data['data']['id']
