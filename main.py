import requests
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import Optional
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from database import get_db
from models import Pokemon, User
from schemas import UserResponse, UserCreate, Token, PokemonGetOutputSchema, PokemonPostPutInputSchema

app = FastAPI()
SECRET_KEY = "a0342e90271446facc8f2b84002a4daa797da99772ad11c3efd488c64706b777"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_bearer = OAuth2PasswordBearer(tokenUrl="/token")

def get_password_hash(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_bearer), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    return user

def role_required(required_role: str):
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role != required_role:
            raise HTTPException(status_code=403, detail="Operation not permitted")
        return current_user
    return role_checker

@app.post("/users/", response_model=UserResponse, summary="Create a new user")
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    hashed_password = get_password_hash(user.password)
    db_user = User(username=user.username, hashed_password=hashed_password, role=user.role)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/token", response_model=Token, summary="Login to get access token")
def login_for_access_token(user: UserCreate, db: Session = Depends(get_db)):
    print(user)
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": db_user.username, "role": db_user.role},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/pokemons/", response_model=PokemonGetOutputSchema, summary="Create a new Pokémon")
def create_pokemon(pokemon: PokemonPostPutInputSchema, db: Session = Depends(get_db), current_user: User = Depends(role_required('admin'))):
    db_pokemon = Pokemon(**pokemon.dict())
    db.add(db_pokemon)
    db.commit()
    db.refresh(db_pokemon)
    return db_pokemon

@app.post("/pokemons/post/", response_model=dict, summary="Load Pokémon data from URL")
def fetch_and_load_pokemons(db: Session = Depends(get_db), current_user: User = Depends(role_required('admin'))):
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

@app.get("/pokemons/{pokemon_id}", response_model=PokemonGetOutputSchema, summary="Get a Pokémon by ID")
def get_pokemon_by_id(pokemon_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    pokemon = db.query(Pokemon).filter(Pokemon.id == pokemon_id).first()
    if pokemon is None:
        raise HTTPException(status_code=404, detail="Pokémon not found")
    return pokemon

@app.put("/pokemons/{pokemon_id}", response_model=PokemonGetOutputSchema, summary="Update a Pokémon by ID")
def update_pokemon(pokemon_id: int, pokemon_update: PokemonPostPutInputSchema, db: Session = Depends(get_db), current_user: User = Depends(role_required('admin'))):
    db_pokemon = db.query(Pokemon).filter(Pokemon.id == pokemon_id).first()
    if db_pokemon is None:
        raise HTTPException(status_code=404, detail="Pokémon not found")

    for key, value in pokemon_update.dict().items():
        setattr(db_pokemon, key, value)

    db.commit()
    db.refresh(db_pokemon)
    return db_pokemon

@app.delete("/pokemons/{pokemon_id}", summary="Delete a Pokémon by ID")
def delete_pokemon(pokemon_id: int, db: Session = Depends(get_db), current_user: User = Depends(role_required('admin'))):
    db_pokemon = db.query(Pokemon).filter(Pokemon.id == pokemon_id).first()
    if db_pokemon is None:
        raise HTTPException(status_code=404, detail="Pokémon not found")

    db.delete(db_pokemon)
    db.commit()
    return {"status": "success", "message": "Pokémon deleted successfully"}
