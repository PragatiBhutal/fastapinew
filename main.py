import requests
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import Optional
from database import SessionLocal
from models import Pokemon

app = FastAPI()

db = SessionLocal()

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

@app.get("/pokemon/{pokemon_id}", response_model=PokemonResponse, summary="Get a Pokémon by ID")
def get_pokemon_by_id(pokemon_id: int):
    pokemon = db.query(Pokemon).filter(Pokemon.id == pokemon_id).first()
    if pokemon is None:
        raise HTTPException(status_code=404, detail="Pokémon not found")
    return pokemon

@app.get("/pokemon", response_model=list[PokemonResponse], summary="List Pokémon with sorting and searching")
def pokemon_list(
    order: str = Query("asc", description="Ordering of Pokémon: 'asc' for ascending or 'desc' for descending"),
    limit: int = Query(10, description="Number of Pokémon to return"),
    keyword: Optional[str] = None,
    column: str = Query("name", description="Column to search in (default is 'name')")
):
    query = db.query(Pokemon)

    if keyword:
        try:
            query = query.filter(getattr(Pokemon, column).ilike(f"%{keyword}%"))
        except AttributeError:
            raise HTTPException(status_code=400, detail=f"Invalid column: {column}")

    if order == "asc":
        query = query.order_by(Pokemon.id.asc())
    elif order == "desc":
        query = query.order_by(Pokemon.id.desc())
    else:
        raise HTTPException(status_code=400, detail="Invalid order parameter. Use 'asc' or 'desc'.")

    pokemons = query.limit(limit).all()

    return pokemons


@app.post("/pokemon", response_model=PokemonResponse, summary="Create a new Pokémon")
def create_pokemon(pokemon: PokemonCreate):
    db_pokemon = Pokemon(**pokemon.dict())
    db.add(db_pokemon)
    db.commit()
    db.refresh(db_pokemon)
    return db_pokemon

@app.post("/pokemon/load", summary="Load Pokémon data from URL")
def fetch_and_load_pokemons():
    url = "https://coralvanda.github.io/pokemon_data.json"
    try:
        response = requests.get(url)
        response.raise_for_status()
        pokemon_data = response.json()

        if not isinstance(pokemon_data, list):
            raise HTTPException(status_code=400, detail="Invalid data format")

        pokemon_mappings = []
        for item in pokemon_data:
            pokemon_mapping = {
                "name": item["Name"],
                "type1": item["Type 1"],
                "type2": item.get("Type 2"),
                "total": item["Total"],
                "hp": item["HP"],
                "attack": item["Attack"],
                "defense": item["Defense"],
                "sp_attack": item["Sp. Atk"],
                "sp_defense": item["Sp. Def"],
                "speed": item["Speed"]
            }
            pokemon_mappings.append(pokemon_mapping)

        db.bulk_insert_mappings(Pokemon, pokemon_mappings)
        print("Pokémon Mappings to be Inserted:", pokemon_mappings)
        db.commit()

        return {"status": "success", "message": "Pokémon data loaded successfully"}

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except KeyError as e:
        raise HTTPException(status_code=400, detail=f"Missing key in data: {e}")


@app.put("/pokemon/{pokemon_id}", response_model=PokemonResponse, summary="Update a Pokémon by ID")
def update_pokemon(pokemon_id: int, pokemon_update: PokemonCreate):
    db_pokemon = db.query(Pokemon).filter(Pokemon.id == pokemon_id).first()
    if db_pokemon is None:
        raise HTTPException(status_code=404, detail="Pokémon not found")

    for key, value in pokemon_update.dict().items():
        setattr(db_pokemon, key, value)

    db.commit()
    db.refresh(db_pokemon)
    return db_pokemon

@app.delete("/pokemon/{pokemon_id}", status_code=204, summary="Delete a Pokémon by ID")
def delete_pokemon(pokemon_id: int):
    db_pokemon = db.query(Pokemon).filter(Pokemon.id == pokemon_id).first()
    if db_pokemon is None:
        raise HTTPException(status_code=404, detail="Pokémon not found")

    db.delete(db_pokemon)
    db.commit()
    return None

