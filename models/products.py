from typing import List
from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import relationship

from models.database import BaseModel
from models.orderproducts import OrderProduct


class Product(BaseModel):
    __tablename__ = "products"

    id = Column(
        Integer, primary_key=True, unique=True, autoincrement=True)
    stock = Column(Integer, default=0, nullable=False)
    name = Column(String(200), unique=True, nullable=False)
    price = Column(Float, nullable=False)
    description = Column(String(200), nullable=True)
    category = Column(String(45), nullable=True)

    # clients = relationship('clients', secondary=OrderProduct.__tablename__,
    #        back_populates='products')
    product_orders = relationship("OrderProduct", back_populates="product")
