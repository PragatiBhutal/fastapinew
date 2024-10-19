from pydantic import BaseModel, Field
from typing import Optional, List


class OurBaseModel(BaseModel):
    class Config:
        orm_mode = True


# Input Schemas for Pokémon
class PokemonPostPutInputSchema(OurBaseModel):
    name: str = Field(min_length=2, max_length=30)
    type_1: str
    type_2: Optional[str] = None
    total: int
    hp: int
    attack: int
    defense: int
    sp_atk: int
    sp_def: int
    speed: int = Field(lt=200, gt=4)
    generation: int = Field(lt=7, gt=0, default=2)
    legendary: bool


# Output Schemas for Pokémon
class PokemonGetOutputSchema(OurBaseModel):
    id: int
    name: str
    type_1: str
    type_2: Optional[str]
    total: int
    hp: int
    attack: int
    defense: int
    sp_atk: int
    sp_def: int
    speed: int
    generation: int
    legendary: bool


class DeleteResponse(OurBaseModel):
    message: str


class PokemonPostPutOutputSchema(PokemonGetOutputSchema):
    pass


class OurBaseModel(BaseModel):
    class Config:
        orm_mode = True


class UserCreate(OurBaseModel):
    username: str
    password: str
    role: Optional[str] = "user"


class UserResponse(OurBaseModel):
    username: str
    role: str


class Token(OurBaseModel):
    access_token: str
    token_type: str
