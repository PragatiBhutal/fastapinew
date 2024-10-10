import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app, Base, get_db

TEST_DATABASE_URL = "postgresql://postgres:password@localhost/test_pokemon_db"

test_engine = create_engine(TEST_DATABASE_URL)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="module", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


client = TestClient(app)


def test_create_pokemon():
    pokemon_data = {
        "name": "Bulbasaur",
        "type1": "Grass",
        "type2": "Poison",
        "total": 318,
        "hp": 45,
        "attack": 49,
        "defense": 49,
        "sp_attack": 65,
        "sp_defense": 65,
        "speed": 45
    }
    response = client.post("/pokemons/", json=pokemon_data)
    assert response.status_code == 200
    assert response.json()["name"] == "Bulbasaur"


def test_get_pokemon_by_existing_id():
    response = client.get("/pokemons/1")
    assert response.status_code == 200
    assert response.json()["name"] == "Bulbasaur"


def test_get_pokemon_by_non_existing_id():
    response = client.get("/pokemons/9999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Pokémon not found"


def test_fetch_and_load_pokemons():
    response = client.post("/pokemons/post/")
    assert response.status_code == 200
    assert response.json()["status"] == "success"


def test_update_pokemon():
    updated_data = {
        "name": "Ivysaur",
        "type1": "Grass",
        "type2": "Poison",
        "total": 405,
        "hp": 60,
        "attack": 62,
        "defense": 63,
        "sp_attack": 80,
        "sp_defense": 80,
        "speed": 60
    }
    response = client.put("/pokemons/1", json=updated_data)
    assert response.status_code == 200
    assert response.json()["name"] == "Ivysaur"


def test_delete_pokemon():
    response = client.delete("/pokemons/1")
    assert response.status_code == 200
    assert response.json()["status"] == "success"


def test_delete_non_existing_pokemon():
    response = client.delete("/pokemons/9999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Pokémon not found"
