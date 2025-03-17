from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base


class Address(Base):
    __tablename__ = "addresses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    city = Column(String, nullable=False)
    street = Column(String, nullable=False)
    house = Column(String, nullable=False)
    apartment = Column(String, nullable=True)

    user = relationship("User", back_populates="addresses")
    order = relationship("Order", back_populates="address", uselist=False)