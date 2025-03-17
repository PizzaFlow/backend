from typing import Optional

from pydantic import BaseModel


class AddressBase(BaseModel):
    city: str
    street: str
    house: str
    apartment: Optional[str] = None

class AddressResponse(AddressBase):
    id: int
    user_id: int
    city: str
    street: str
    house: str
    apartment: Optional[str] = None

    class Config:
        from_attributes = True
