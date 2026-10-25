def test_create_medical_record(auth_client, test_member):
    res = auth_client.post('/api/records/', json={
        'family_member_id': test_member,
        'title': 'Lipid Profile Report',
        'record_type': 'Lab Test',
        'record_date': '2026-08-10',
        'doctor': 'Dr. Gupta',
        'hospital': 'Max Healthcare',
        'description': 'Cholesterol levels check',
        'diagnosis': 'Normal',
        'notes': 'Repeat after 6 months',
        'tags': 'cholesterol,blood'
    })
    assert res.status_code == 200
    data = res.get_json()
    assert data['success'] is True
    assert 'id' in data['data']

def test_list_medical_records(auth_client, test_member):
    # Create a record first
    auth_client.post('/api/records/', json={
        'family_member_id': test_member,
        'title': 'General Wellness Check',
        'record_type': 'Doctor Visit',
        'record_date': '2026-09-01'
    })

    res = auth_client.get(f'/api/records/?member_id={test_member}')
    assert res.status_code == 200
    data = res.get_json()
    assert data['success'] is True
    assert isinstance(data['data'], list)
    assert len(data['data']) >= 1

def test_get_medical_record(auth_client, test_member):
    create_res = auth_client.post('/api/records/', json={
        'family_member_id': test_member,
        'title': 'X-Ray Knee',
        'record_type': 'Scan',
        'record_date': '2026-07-15'
    })
    rec_id = create_res.get_json()['data']['id']

    res = auth_client.get(f'/api/records/{rec_id}')
    assert res.status_code == 200
    data = res.get_json()
    assert data['success'] is True
    assert data['data']['title'] == 'X-Ray Knee'

def test_update_medical_record(auth_client, test_member):
    create_res = auth_client.post('/api/records/', json={
        'family_member_id': test_member,
        'title': 'Draft Record',
        'record_type': 'Other',
        'record_date': '2026-07-01'
    })
    rec_id = create_res.get_json()['data']['id']

    up_res = auth_client.put(f'/api/records/{rec_id}', json={
        'title': 'Finalized Record',
        'diagnosis': 'Clear'
    })
    assert up_res.status_code == 200
    assert up_res.get_json()['success'] is True

    get_res = auth_client.get(f'/api/records/{rec_id}')
    assert get_res.get_json()['data']['title'] == 'Finalized Record'

def test_delete_medical_record(auth_client, test_member):
    create_res = auth_client.post('/api/records/', json={
        'family_member_id': test_member,
        'title': 'Record to Delete',
        'record_type': 'Other',
        'record_date': '2026-07-01'
    })
    rec_id = create_res.get_json()['data']['id']

    del_res = auth_client.delete(f'/api/records/{rec_id}')
    assert del_res.status_code == 200
    assert del_res.get_json()['success'] is True

    get_res = auth_client.get(f'/api/records/{rec_id}')
    assert get_res.status_code == 404
