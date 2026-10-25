def test_create_medicine(auth_client, test_member):
    res = auth_client.post('/api/medicines/', json={
        'family_member_id': test_member,
        'name': 'Metformin 500mg',
        'dosage': '500mg',
        'frequency': 'Twice daily',
        'start_date': '2026-01-01',
        'instructions': 'Take with meals',
        'status': 'active'
    })
    assert res.status_code == 200
    data = res.get_json()
    assert data['success'] is True
    assert 'id' in data['data']

def test_list_medicines(auth_client, test_member):
    auth_client.post('/api/medicines/', json={
        'family_member_id': test_member,
        'name': 'Aspirin 75mg',
        'dosage': '75mg',
        'status': 'active'
    })
    res = auth_client.get('/api/medicines/')
    assert res.status_code == 200
    data = res.get_json()
    assert data['success'] is True
    assert isinstance(data['data'], list)
    assert len(data['data']) >= 1

def test_update_medicine_status(auth_client, test_member):
    create_res = auth_client.post('/api/medicines/', json={
        'family_member_id': test_member,
        'name': 'Paracetamol 650mg',
        'status': 'active'
    })
    med_id = create_res.get_json()['data']['id']

    up_res = auth_client.put(f'/api/medicines/{med_id}/status', json={
        'status': 'completed'
    })
    assert up_res.status_code == 200
    assert up_res.get_json()['success'] is True

    get_res = auth_client.get(f'/api/medicines/{med_id}')
    assert get_res.get_json()['data']['status'] == 'completed'

def test_delete_medicine(auth_client, test_member):
    create_res = auth_client.post('/api/medicines/', json={
        'family_member_id': test_member,
        'name': 'Antacid Tablet',
        'status': 'active'
    })
    med_id = create_res.get_json()['data']['id']

    del_res = auth_client.delete(f'/api/medicines/{med_id}')
    assert del_res.status_code == 200

    check_res = auth_client.get(f'/api/medicines/{med_id}')
    assert check_res.status_code == 404
