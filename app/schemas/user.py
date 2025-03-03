from typing import List, Optional

from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: str
    password: str


# Ингредиент
class IngredientBase(BaseModel):
    name: str
    price: float

class IngredientResponse(IngredientBase):
    id: int

    class Config:
        from_attributes = True  # Pydantic V2

# Пицца
class PizzaBase(BaseModel):
    name: str
    price: float
    description: str

class PizzaResponse(PizzaBase):
    id: int
    ingredients: List[IngredientResponse]

    class Config:
        from_attributes = True

# Адрес
class AddressBase(BaseModel):
    city: str
    street: str
    house: str
    apartment: Optional[str] = None

class AddressResponse(AddressBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True

# Пользователь (минимальная информация)
class UserBase(BaseModel):
    username: str
    email: str

class UserResponse(UserBase):
    id: int

    class Config:
        from_attributes = True