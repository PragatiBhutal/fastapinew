from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

from database import engine, Base, get_db
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
    get_current_user, ACCESS_TOKEN_EXPIRE_MINUTES,
)

app = FastAPI()

Base.metadata.create_all(bind=engine)


@app.post("/register", response_model=UserResponse)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    hashed_password = get_password_hash(user.password)
    db_user = User(username=user.username, hashed_password=hashed_password, role=user.role)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@app.post("/token", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/pokemons/", response_model=list[PokemonGetOutputSchema])
def get_all_pokemons(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    pokemons = db.query(Pokemon).all()
    return pokemons


@app.post("/pokemons/", response_model=PokemonGetOutputSchema)
def create_pokemon(pokemon: PokemonPostPutInputSchema, db: Session = Depends(get_db),
                   current_user: User = Depends(get_current_user)):
    db_pokemon = Pokemon(**pokemon.dict())
    db.add(db_pokemon)
    db.commit()
    db.refresh(db_pokemon)
    return db_pokemon


@app.put("/pokemons/{pokemon_id}", response_model=PokemonGetOutputSchema, summary="Update a Pokémon by ID")
def update_pokemon(pokemon_id: int, pokemon_update: PokemonPostPutInputSchema, db: Session = Depends(get_db),
                   current_user: User = Depends(get_current_user)):
    db_pokemon = db.query(Pokemon).filter(Pokemon.id == pokemon_id).first()
    if db_pokemon is None:
        raise HTTPException(status_code=404, detail="Pokémon not found")

    for key, value in pokemon_update.dict().items():
        setattr(db_pokemon, key, value)

    db.commit()
    db.refresh(db_pokemon)
    return db_pokemon


@app.delete("/pokemons/{pokemon_id}", response_model=DeleteResponse, summary="Delete a Pokémon by ID")
def delete_pokemon(pokemon_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_pokemon = db.query(Pokemon).filter(Pokemon.id == pokemon_id).first()
    if db_pokemon is None:
        raise HTTPException(status_code=404, detail="Pokémon not found")

    db.delete(db_pokemon)
    db.commit()
    return DeleteResponse(message="Pokémon deleted successfully")
