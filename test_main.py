import pytest
from fastapi.testclient import TestClient
from main import app
from test_Data import generate_pokemon_data

client = TestClient(app)

def test_create_pokemon():
    pokemon_data = generate_pokemon_data()
    response = client.post("/pokemons/", json=pokemon_data)
    assert response.status_code == 200
    assert response.json()["name"] == pokemon_data["name"]

def test_get_pokemon_by_existing_id():
    # Create a Pokémon to get
    data = generate_pokemon_data()
    create_response = client.post("/pokemons/", json=data)
    pokemon_id = create_response.json()["id"]

    response = client.get(f"/pokemons/{pokemon_id}")
    assert response.status_code == 200
    assert response.json()["name"] == data["name"]

def test_get_pokemon_by_non_existing_id():
    response = client.get("/pokemons/9999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Pokémon not found"

def test_fetch_and_load_pokemons():
    response = client.post("/pokemons/post/")
    assert response.status_code == 200
    assert response.json()["status"] == "success"

def test_update_pokemon():
    data = generate_pokemon_data()
    create_response = client.post("/pokemons/", json=data)
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
    response = client.put(f"/pokemons/{pokemon_id}", json=updated_data)
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Pokémon"

def test_update_non_existing_pokemon():
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
    response = client.put("/pokemons/9999", json=updated_data)
    assert response.status_code == 404
    assert response.json()["detail"] == "Pokémon not found"

def test_delete_pokemon():
    # Create a Pokémon to delete
    data = generate_pokemon_data()
    create_response = client.post("/pokemons/", json=data)
    pokemon_id = create_response.json()["id"]

    response = client.delete(f"/pokemons/{pokemon_id}")
    assert response.status_code == 200
    assert response.json()["status"] == "success"

def test_delete_non_existing_pokemon():
    response = client.delete("/pokemons/9999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Pokémon not found"
