from sqlalchemy import func
from sqlalchemy.orm import relationship
from models.database import BaseModel
from sqlalchemy import Column, Integer, String, DateTime


class Client(BaseModel):
    __tablename__ = "clients"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    phone = Column(String(12), nullable=True)
    address = Column(String(100), nullable=True)
    registered_on = Column(DateTime(
        timezone=True), nullable=False, default=func.now())

    client_orders = relationship("OrderProduct", back_populates="order")
    # products = relationship('products', secondary=OrderProduct.__tablename__,
    #                     back_populates='clients')

    def __init__(self, name, email, phone=None, address=None):
        self.name = name
        self.email = email
        self.phone = phone
        self.address = address
