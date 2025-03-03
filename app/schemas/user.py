from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class UserBase(BaseModel):
    username: str
    email: str

class UserResponse(UserBase):
    id: int

    class Config:
        from_attributes = True