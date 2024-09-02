from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
import requests

from database import engine, Base, get_db
from models import Pokemon

app = FastAPI()


class PokemonCreate(BaseModel):
    name: str
    type1: str
    type2: Optional[str] = None
    total: int
    hp: int
    attack: int
    defense: int
    sp_attack: int
    sp_defense: int
    speed: int


class PokemonResponse(PokemonCreate):
    id: int

    class Config:
        orm_mode = True


@app.post("/pokemons/", response_model=PokemonResponse, summary="Create a new Pokémon")
def create_pokemon(pokemon: PokemonCreate, db: Session = Depends(get_db)):
    db_pokemon = Pokemon(**pokemon.dict())
    db.add(db_pokemon)
    db.commit()
    db.refresh(db_pokemon)
    return db_pokemon


@app.post("/pokemons/post/", response_model=dict, summary="load Pokémon data from URL")
def fetch_and_load_pokemons(db: Session = Depends(get_db)):
    url = "https://coralvanda.github.io/pokemon_data.json"
    try:
        response = requests.get(url)
        response.raise_for_status()
        pokemon_data = response.json()

        if not isinstance(pokemon_data, list):
            raise HTTPException(status_code=400, detail="Invalid data format")

        for item in pokemon_data:
            pokemon = Pokemon(
                name=item["Name"],
                type1=item["Type 1"],
                type2=item.get("Type 2"),
                total=item["Total"],
                hp=item["HP"],
                attack=item["Attack"],
                defense=item["Defense"],
                sp_attack=item["Sp. Atk"],
                sp_defense=item["Sp. Def"],
                speed=item["Speed"]
            )
            db.add(pokemon)

        db.commit()
        return {"status": "success", "message": "Pokémon data loaded successfully"}

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except KeyError as e:
        raise HTTPException(status_code=400, detail=f"Missing key in data: {e}")


@app.get("/pokemons/{pokemon_id}", response_model=PokemonResponse, summary="Get a Pokémon by ID")
def get_pokemon_by_id(pokemon_id: int, db: Session = Depends(get_db)):
    pokemon = db.query(Pokemon).filter(Pokemon.id == pokemon_id).first()
    if pokemon is None:
        raise HTTPException(status_code=404, detail="Pokémon not found")
    return pokemon


@app.put("/pokemons/{pokemon_id}", response_model=PokemonResponse, summary="Update a Pokémon by ID")
def update_pokemon(pokemon_id: int, pokemon_update: PokemonCreate, db: Session = Depends(get_db)):
    db_pokemon = db.query(Pokemon).filter(Pokemon.id == pokemon_id).first()
    if db_pokemon is None:
        raise HTTPException(status_code=404, detail="Pokémon not found")

    for key, value in pokemon_update.dict().items():
        setattr(db_pokemon, key, value)

    db.commit()
    db.refresh(db_pokemon)
    return db_pokemon


@app.delete("/pokemons/{pokemon_id}", summary="Delete a Pokémon by ID")
def delete_pokemon(pokemon_id: int, db: Session = Depends(get_db)):
    db_pokemon = db.query(Pokemon).filter(Pokemon.id == pokemon_id).first()
    if db_pokemon is None:
        raise HTTPException(status_code=404, detail="Pokémon not found")

    db.delete(db_pokemon)
    db.commit()
    return {"status": "success", "message": "Pokémon deleted successfully"}
