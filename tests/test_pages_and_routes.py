import pytest

def test_all_pages_render(auth_client, test_member):
    pages = [
        '/dashboard',
        '/family',
        f'/member/{test_member}',
        '/records',
        '/medicines',
        '/reminders',
        '/appointments',
        '/tests',
        '/vaccinations',
        '/health-tracker',
        '/timeline',
        '/expenses',
        '/insurance',
        '/emergency',
        '/notifications',
        '/search',
        '/settings'
    ]
    for page in pages:
        res = auth_client.get(page)
        assert res.status_code == 200, f"Page {page} failed to render (status {res.status_code})"

def test_all_api_endpoints_respond(auth_client, test_member):
    endpoints = [
        '/api/family-members/',
        f'/api/family-members/{test_member}',
        f'/api/family-members/{test_member}/summary',
        '/api/records/',
        '/api/medicines/',
        '/api/reminders/',
        '/api/appointments/',
        '/api/tests/',
        '/api/vaccinations/',
        '/api/health-parameters/',
        '/api/health-parameters/trends',
        '/api/expenses/',
        '/api/expenses/summary',
        '/api/insurance/policies',
        '/api/insurance/claims',
        '/api/timeline',
        '/api/emergency/all',
        f'/api/emergency/{test_member}',
        '/api/notifications',
        '/api/search?q=test'
    ]
    for ep in endpoints:
        res = auth_client.get(ep)
        assert res.status_code == 200, f"API {ep} returned {res.status_code}"
