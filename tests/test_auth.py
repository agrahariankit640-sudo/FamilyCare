import json

def test_register_success(client):
    res = client.post('/api/auth/register', json={
        'name': 'Aanya Verma',
        'email': 'aanya@example.com',
        'phone': '9876543210',
        'password': 'Password@123'
    })
    assert res.status_code == 201
    data = res.get_json()
    assert data['success'] is True
    assert 'id' in data['data']

def test_register_duplicate_email(client):
    client.post('/api/auth/register', json={
        'name': 'Duplicate User',
        'email': 'duplicate@example.com',
        'phone': '9876543210',
        'password': 'Password@123'
    })
    res = client.post('/api/auth/register', json={
        'name': 'Duplicate User 2',
        'email': 'duplicate@example.com',
        'phone': '9876543211',
        'password': 'Password@123'
    })
    assert res.status_code == 400
    data = res.get_json()
    assert 'error' in data

def test_register_missing_fields(client):
    res = client.post('/api/auth/register', json={
        'email': 'incomplete@example.com'
    })
    assert res.status_code == 400
    data = res.get_json()
    assert 'error' in data

def test_login_success(client, registered_user):
    res = client.post('/api/auth/login', json={
        'email': registered_user['email'],
        'password': registered_user['password']
    })
    assert res.status_code == 200
    data = res.get_json()
    assert data['success'] is True
    assert data['data']['email'] == registered_user['email']
    assert 'password_hash' not in data['data']

def test_login_wrong_password(client, registered_user):
    res = client.post('/api/auth/login', json={
        'email': registered_user['email'],
        'password': 'WrongPassword@999'
    })
    assert res.status_code == 401
    data = res.get_json()
    assert 'error' in data

def test_login_nonexistent_user(client):
    res = client.post('/api/auth/login', json={
        'email': 'nobody_exists@example.com',
        'password': 'Password@123'
    })
    assert res.status_code == 401

def test_me_authenticated(auth_client, registered_user):
    res = auth_client.get('/api/auth/me')
    assert res.status_code == 200
    data = res.get_json()
    assert data['success'] is True
    assert data['data']['email'] == registered_user['email']

def test_logout(auth_client):
    res = auth_client.post('/api/auth/logout')
    assert res.status_code == 200
    data = res.get_json()
    assert data['success'] is True

def test_access_protected_route_unauthenticated(client):
    res = client.get('/api/family-members/')
    assert res.status_code in [302, 401]

def test_change_password(auth_client, registered_user):
    res = auth_client.put('/api/auth/password', json={
        'old_password': registered_user['password'],
        'new_password': 'NewPassword@456'
    })
    assert res.status_code == 200
    data = res.get_json()
    assert data['success'] is True

    # Check login with new password
    auth_client.post('/api/auth/logout')
    res_login = auth_client.post('/api/auth/login', json={
        'email': registered_user['email'],
        'password': 'NewPassword@456'
    })
    assert res_login.status_code == 200
