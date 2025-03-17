from typing import Optional

from pydantic import BaseModel, EmailStr, constr, Field


class UserCreate(BaseModel):
    email: EmailStr
    password: Optional[constr(min_length=5)]

class UserEditSchema(BaseModel):
    username: Optional[str] = Field(None, min_length=1, max_length=25)
    password: Optional[str] = Field(None, min_length=5)
    phone_number: Optional[str] = Field(None, pattern=r"^(?:\+7|8)\d{10}$")

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserBase(BaseModel):
    username: str
    email: str

class UserResponseForRegistration(BaseModel):
    id: int
    email: str

    class Config:
        from_attributes = True

class UserResponse(BaseModel):
    id: int
    email: str | None = None
    username: str | None = None
    phone_number: str | None = None

    class Config:
        from_attributes = True
