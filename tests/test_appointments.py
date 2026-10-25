def test_create_appointment(auth_client, test_member):
    res = auth_client.post('/api/appointments/', json={
        'family_member_id': test_member,
        'doctor_name': 'Dr. Raman',
        'hospital': 'City Hospital',
        'specialization': 'General Physician',
        'visit_date': '2026-10-15',
        'visit_time': '11:00',
        'reason': 'Annual physical',
        'status': 'upcoming'
    })
    assert res.status_code == 200
    data = res.get_json()
    assert data['success'] is True
    assert 'id' in data['data']

def test_list_appointments(auth_client, test_member):
    auth_client.post('/api/appointments/', json={
        'family_member_id': test_member,
        'doctor_name': 'Dr. Neha',
        'visit_date': '2026-10-20',
        'status': 'upcoming'
    })
    res = auth_client.get('/api/appointments/')
    assert res.status_code == 200
    data = res.get_json()
    assert data['success'] is True
    assert isinstance(data['data'], list)
    assert len(data['data']) >= 1

def test_update_appointment(auth_client, test_member):
    create_res = auth_client.post('/api/appointments/', json={
        'family_member_id': test_member,
        'doctor_name': 'Dr. Kapoor',
        'visit_date': '2026-10-25',
        'status': 'upcoming'
    })
    appt_id = create_res.get_json()['data']['id']

    up_res = auth_client.put(f'/api/appointments/{appt_id}', json={
        'status': 'completed',
        'notes': 'All vitals normal'
    })
    assert up_res.status_code == 200

    get_res = auth_client.get(f'/api/appointments/{appt_id}')
    assert get_res.get_json()['data']['status'] == 'completed'

def test_delete_appointment(auth_client, test_member):
    create_res = auth_client.post('/api/appointments/', json={
        'family_member_id': test_member,
        'doctor_name': 'Dr. Temporary',
        'visit_date': '2026-10-30',
        'status': 'cancelled'
    })
    appt_id = create_res.get_json()['data']['id']

    del_res = auth_client.delete(f'/api/appointments/{appt_id}')
    assert del_res.status_code == 200

    check_res = auth_client.get(f'/api/appointments/{appt_id}')
    assert check_res.status_code == 404
