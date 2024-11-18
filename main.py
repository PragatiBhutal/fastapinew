import requests
from fastapi import FastAPI, Depends, HTTPException, status, Query
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from pydantic import BaseModel
from typing import Optional

from database import engine, Base, get_db, SessionLocal
from models import Pokemon, User
from schemas import (
    PokemonPostPutInputSchema,
    PokemonGetOutputSchema,
    DeleteResponse,
    UserCreate,
    UserResponse,
    Token,
)
from auth import (
    authenticate_user,
    create_access_token,
    get_password_hash,
    get_current_user,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)

app = FastAPI()

Base.metadata.create_all(bind=engine)

db = SessionLocal()


@app.post("/register", response_model=UserResponse)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username, hashed_password=hashed_password, role=user.role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@app.post("/token", response_model=Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role},
        expires_delta=access_token_expires,
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get(
    "/pokemon/{pokemon_id}",
    response_model=PokemonGetOutputSchema,
    summary="Get a Pokémon by ID",
)
def get_pokemon_by_id(pokemon_id: int):
    pokemon = db.query(Pokemon).filter(Pokemon.id == pokemon_id).first()
    if pokemon is None:
        raise HTTPException(status_code=404, detail="Pokémon not found")
    return pokemon


@app.get(
    "/pokemon",
    response_model=list[PokemonGetOutputSchema],
    summary="List Pokémon with sorting and searching",
)
def pokemon_list(
    order: str = Query(
        "asc",
        description="Ordering of Pokémon: 'asc' for ascending or 'desc' for descending",
    ),
    limit: int = Query(10, description="Number of Pokémon to return"),
    keyword: Optional[str] = None,
    column: str = Query("name", description="Column to search in (default is 'name')"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
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
        raise HTTPException(
            status_code=400, detail="Invalid order parameter. Use 'asc' or 'desc'."
        )

    pokemons = query.limit(limit).all()

    return pokemons


@app.post("/pokemon/load", summary="Load Pokémon data from URL")
def fetch_and_load_pokemons(db: Session = Depends(get_db)):
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
                "sp_atk": item["Sp. Atk"],
                "sp_def": item["Sp. Def"],
                "speed": item["Speed"],
                "generation": item["Generation"],
                "legendary": item["Legendary"],
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


@app.post(
    "/pokemon", response_model=PokemonGetOutputSchema, summary="Create a new Pokémon"
)
def create_pokemon(
    pokemon: PokemonPostPutInputSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_pokemon = Pokemon(**pokemon.dict())
    db.add(db_pokemon)
    db.commit()
    db.refresh(db_pokemon)
    return db_pokemon


@app.put(
    "/pokemon/{pokemon_id}",
    response_model=PokemonGetOutputSchema,
    summary="Update a Pokémon by ID",
)
def update_pokemon(
    pokemon_id: int,
    pokemon_update: PokemonPostPutInputSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_pokemon = db.query(Pokemon).filter(Pokemon.id == pokemon_id).first()
    if db_pokemon is None:
        raise HTTPException(status_code=404, detail="Pokémon not found")

    for key, value in pokemon_update.dict().items():
        setattr(db_pokemon, key, value)

    db.commit()
    db.refresh(db_pokemon)
    return db_pokemon


@app.delete(
    "/pokemon/{pokemon_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a Pokémon by ID",
)
def delete_pokemon(
    pokemon_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_pokemon = db.query(Pokemon).filter(Pokemon.id == pokemon_id).first()
    if db_pokemon is None:
        raise HTTPException(status_code=404, detail="Pokémon not found")

    db.delete(db_pokemon)
    db.commit()
    return None
