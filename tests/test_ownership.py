def test_user_cannot_access_other_users_family_member(app, auth_client, test_member):
    # test_member belongs to 'tester@example.com' (auth_client)

    # Register and login as a second user on a separate test client
    client2 = app.test_client()
    client2.post('/api/auth/register', json={
        'name': 'Second User',
        'email': 'second@example.com',
        'password': 'Password@123',
        'phone': '9111111111'
    })
    client2.post('/api/auth/login', json={
        'email': 'second@example.com',
        'password': 'Password@123'
    })

    # Second user tries to get User 1's family member
    res_get = client2.get(f'/api/family-members/{test_member}')
    assert res_get.status_code == 404

    # Second user listing members should not see User 1's members
    res_list = client2.get('/api/family-members/')
    assert res_list.status_code == 200
    ids = [m['id'] for m in res_list.get_json()['data']]
    assert test_member not in ids

    # Second user cannot update User 1's family member
    res_update = client2.put(f'/api/family-members/{test_member}', json={'name': 'Hacked Name'})
    assert res_update.status_code in [400, 404]

    # Second user cannot delete User 1's family member
    res_delete = client2.delete(f'/api/family-members/{test_member}')
    assert res_delete.status_code in [400, 404]

    # Verify original member is unchanged when accessed by original owner
    original_check = auth_client.get(f'/api/family-members/{test_member}')
    assert original_check.status_code == 200
    assert original_check.get_json()['data']['name'] == 'Arun Sharma'

def test_user_cannot_access_other_users_medical_records(app, auth_client, test_member):
    # Create medical record under User 1
    create_rec = auth_client.post('/api/records/', json={
        'family_member_id': test_member,
        'title': 'Confidential Lab Report',
        'record_type': 'Lab Test',
        'record_date': '2026-08-01'
    })
    rec_id = create_rec.get_json()['data']['id']

    # Login as second user on a separate test client
    client2 = app.test_client()
    client2.post('/api/auth/register', json={
        'name': 'Other User',
        'email': 'other@example.com',
        'password': 'Password@123',
        'phone': '9222222222'
    })
    client2.post('/api/auth/login', json={
        'email': 'other@example.com',
        'password': 'Password@123'
    })

    # Second user cannot view User 1's record
    res = client2.get(f'/api/records/{rec_id}')
    assert res.status_code == 404

    # Second user cannot update User 1's record
    res_up = client2.put(f'/api/records/{rec_id}', json={'title': 'Compromised'})
    assert res_up.status_code in [400, 404]

    # Second user cannot delete User 1's record
    res_del = client2.delete(f'/api/records/{rec_id}')
    assert res_del.status_code in [400, 404]
