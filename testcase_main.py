import pytest
from fastapi.testclient import TestClient
from main import app
from test_data import generate_pokemon_data

client = TestClient(app)


def get_access_token(username: str = "testuser", password: str = "testpassword"):
    response = client.post("/register", json={"username": username, "password": password})
    assert response.status_code == 200

    response = client.post("/token", data={"username": username, "password": password})
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture(scope="module")
def token():
    return get_access_token()


def test_create_pokemon(token):
    pokemon_data = generate_pokemon_data()
    response = client.post("/pokemons/", json=pokemon_data, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["name"] == pokemon_data["name"]


def test_get_pokemon_by_existing_id(token):
    # Create a Pokémon to get
    data = generate_pokemon_data()
    create_response = client.post("/pokemons/", json=data, headers={"Authorization": f"Bearer {token}"})
    pokemon_id = create_response.json()["id"]

    response = client.get(f"/pokemons/{pokemon_id}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["name"] == data["name"]


def test_get_pokemon_by_non_existing_id(token):
    response = client.get("/pokemons/9999", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 404
    assert response.json()["detail"] == "Pokémon not found"


def test_update_pokemon(token):
    data = generate_pokemon_data()
    create_response = client.post("/pokemons/", json=data, headers={"Authorization": f"Bearer {token}"})
    pokemon_id = create_response.json()["id"]

    updated_data = {
        "name": "Updated Pokémon",
        "type1": "Updated Type 1",
        "type2": "Updated Type 2",
        "total": 400,
        "hp": 60,
        "attack": 60,
        "defense": 60,
        "sp_attack": 80,
        "sp_defense": 80,
        "speed": 60,
    }
    response = client.put(f"/pokemons/{pokemon_id}", json=updated_data, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Pokémon"


def test_update_non_existing_pokemon(token):
    updated_data = {
        "name": "Updated Pokémon",
        "type1": "Updated Type 1",
        "type2": "Updated Type 2",
        "total": 400,
        "hp": 60,
        "attack": 60,
        "defense": 60,
        "sp_attack": 80,
        "sp_defense": 80,
        "speed": 60,
    }
    response = client.put("/pokemons/9999", json=updated_data, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 404
    assert response.json()["detail"] == "Pokémon not found"


def test_delete_pokemon(token):
    data = generate_pokemon_data()
    create_response = client.post("/pokemons/", json=data, headers={"Authorization": f"Bearer {token}"})
    pokemon_id = create_response.json()["id"]

    response = client.delete(f"/pokemons/{pokemon_id}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["message"] == "Pokémon deleted successfully"


def test_delete_non_existing_pokemon(token):
    response = client.delete("/pokemons/9999", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 404
    assert response.json()["detail"] == "Pokémon not found"


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
