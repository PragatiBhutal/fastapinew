import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def get_access_token(username: str = "testuser", password: str = "testpassword"):
    client.post("/register", json={"username": username, "password": password})
    response = client.post("/token", data={"username": username, "password": password})
    assert response.status_code == 200
    return response.json()["access_token"]


def test_register_user():
    response = client.post("/register", json={"username": "newuser", "password": "newpassword"})
    assert response.status_code == 200
    assert response.json()["username"] == "newuser"

def test_login_user():
    response = client.post("/token", data={"username": "newuser", "password": "newpassword"})
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_with_invalid_credentials():
    response = client.post("/token", data={"username": "wronguser", "password": "wrongpassword"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password"


def test_access_with_invalid_token():
    response = client.get("/pokemons/", headers={"Authorization": "Bearer invalidtoken"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials"


@pytest.fixture(scope="module")
def token():
    return get_access_token()
