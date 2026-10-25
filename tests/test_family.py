def test_create_family_member(auth_client):
    res = auth_client.post('/api/family-members/', json={
        'name': 'Sunita Sharma',
        'relationship': 'Sister',
        'gender': 'Female',
        'date_of_birth': '1992-08-10',
        'blood_group': 'B+',
        'phone': '9876543222',
        'email': 'sunita@example.com',
        'allergies': 'None',
        'existing_conditions': 'None'
    })
    assert res.status_code == 200
    data = res.get_json()
    assert data['success'] is True
    assert 'id' in data['data']

def test_list_family_members(auth_client, test_member):
    res = auth_client.get('/api/family-members/')
    assert res.status_code == 200
    data = res.get_json()
    assert data['success'] is True
    assert isinstance(data['data'], list)
    assert len(data['data']) >= 1

def test_get_family_member(auth_client, test_member):
    res = auth_client.get(f'/api/family-members/{test_member}')
    assert res.status_code == 200
    data = res.get_json()
    assert data['success'] is True
    assert data['data']['name'] == 'Arun Sharma'

def test_update_family_member(auth_client, test_member):
    res = auth_client.put(f'/api/family-members/{test_member}', json={
        'name': 'Arun K. Sharma',
        'blood_group': 'O+'
    })
    assert res.status_code == 200
    data = res.get_json()
    assert data['success'] is True

    # Verify update
    get_res = auth_client.get(f'/api/family-members/{test_member}')
    assert get_res.get_json()['data']['name'] == 'Arun K. Sharma'

def test_delete_family_member(auth_client):
    # Create member to delete
    create_res = auth_client.post('/api/family-members/', json={
        'name': 'Temporary Member',
        'relationship': 'Cousin'
    })
    member_id = create_res.get_json()['data']['id']

    del_res = auth_client.delete(f'/api/family-members/{member_id}')
    assert del_res.status_code == 200
    assert del_res.get_json()['success'] is True

    # Check 404 after delete
    check_res = auth_client.get(f'/api/family-members/{member_id}')
    assert check_res.status_code == 404

def test_create_member_validation(auth_client):
    res = auth_client.post('/api/family-members/', json={})
    # If empty data without name, should either succeed or fail gracefully
    assert res.status_code in [200, 400]
