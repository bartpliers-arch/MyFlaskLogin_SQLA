import pytest
from app import app
from database import db

# Fixture: tworzy czystą bazę danych przed każdym testem
@pytest.fixture
def client():
    with app.app_context():
        db.drop_all()     # usuń wszystkie tabele
        db.create_all()   # stwórz je od nowa
        with app.test_client() as client:
            yield client
        db.session.remove()
        db.drop_all()     # wyczyść po teście

# Test: GET /user/ — lista użytkowników
def test_get_users(client):
    response = client.get('/user/')
    assert response.status_code == 200

# Test: POST /user/ — tworzenie użytkownika
def test_create_user(client):
    payload = {
        "username": "Testowy",
        "email": "testowy@example.com",
        "password": "12345678"
    }
    response = client.post('/user/', json=payload)
    assert response.status_code == 201
    data = response.get_json()
    assert data['username'] == "Testowy"
    assert data['email'] == "testowy@example.com"

# Test: GET /user/<id>/ — pobieranie użytkownika
def test_get_user_by_id(client):
    payload = {
        "username": "RZuser",
        "email": "rz@example.com",
        "password": "rzpassword"
    }
    post_response = client.post('/user/', json=payload)
    user_id = post_response.get_json()['id']

    get_response = client.get(f'/user/{user_id}/')
    assert get_response.status_code == 200
    data = get_response.get_json()
    assert data['username'] == "RZuser"
    assert data['email'] == "rz@example.com"

# Test: GET /user/<id>/ — nieistniejący użytkownik
def test_get_user_invalid_id(client):
    response = client.get('/user/999/')
    assert response.status_code == 404
    data = response.get_json()
    assert data['message'] == 'user not found'

# Test: POST /user/ — zły email
def test_create_user_invalid_email(client):
    payload = {
        "username": "BadEmail",
        "email": "bademail.com",
        "password": "12345678"
    }
    response = client.post('/user/', json=payload)
    assert response.status_code == 400
    assert 'Invalid email' in response.get_json()['message']

# Test: POST /user/ — za krótkie hasło
def test_create_user_short_password(client):
    payload = {
        "username": "ShortPass",
        "email": "short@example.com",
        "password": "123"
    }
    response = client.post('/user/', json=payload)
    assert response.status_code == 400
    assert 'Password' in response.get_json()['message']

# Test: PUT /user/<id>/ — pełna aktualizacja
def test_put_user(client):
    payload = {
        "username": "PutUser",
        "email": "put@example.com",
        "password": "putpass123"
    }
    post_response = client.post('/user/', json=payload)
    user_id = post_response.get_json()['id']

    updated = {
        "username": "UpdatedUser",
        "email": "updated@example.com",
        "password": "newpass123"
    }
    put_response = client.put(f'/user/{user_id}/', json=updated)
    assert put_response.status_code == 200
    data = put_response.get_json()
    assert data['username'] == "UpdatedUser"
    assert data['email'] == "updated@example.com"

# Test: PATCH /user/<id>/ — częściowa aktualizacja
def test_patch_user(client):
    payload = {
        "username": "PatchUser",
        "email": "patch@example.com",
        "password": "patchpass123"
    }
    post_response = client.post('/user/', json=payload)
    user_id = post_response.get_json()['id']

    patch_payload = {
        "username": "PatchedName"
    }
    patch_response = client.patch(f'/user/{user_id}/', json=patch_payload)
    assert patch_response.status_code == 200
    data = patch_response.get_json()
    assert data['username'] == "PatchedName"

# Test: DELETE /user/<id>/ — usunięcie użytkownika
def test_delete_user(client):
    payload = {
        "username": "DeleteUser",
        "email": "delete@example.com",
        "password": "deletepass123"
    }
    post_response = client.post('/user/', json=payload)
    user_id = post_response.get_json()['id']

    delete_response = client.delete(f'/user/{user_id}/')
    assert delete_response.status_code == 200
    assert delete_response.get_json()['message'] == 'user deleted'

    # Sprawdź, czy użytkownik został usunięty
    get_response = client.get(f'/user/{user_id}/')
    assert get_response.status_code == 404
