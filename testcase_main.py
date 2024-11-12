from fastapi.testclient import TestClient
from main import app
from test_data import generate_pokemon_data
from test_auth import token

client = TestClient(app)


def test_create_pokemon(token):
    pokemon_data = generate_pokemon_data()
    response = client.post("/pokemons/", json=pokemon_data, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["name"] == pokemon_data["name"]


def test_get_pokemon_by_existing_id(token):
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
        "sp_atk": 80,
        "sp_def": 80,
        "speed": 60,
        "generation": 4,
        "legendary": "false",
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
        "sp_atk": 80,
        "sp_def": 80,
        "speed": 60,
        "generation": 4,
        "legendary": "false",
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
