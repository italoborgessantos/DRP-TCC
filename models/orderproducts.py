from models.database import BaseModel
from sqlalchemy import func, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, Float, String, DateTime


class OrderProduct(BaseModel):
    __tablename__ = "order_products"
    id = Column(Integer, primary_key=True,
                unique=True, autoincrement=True)
    order_client = Column(
        Integer, ForeignKey('clients.id'), nullable=False)
    order_product = Column(
        Integer, ForeignKey('products.id'), nullable=False)
    order_quantity = Column(Integer, nullable=False, default=1)

    description = Column(String(255), nullable=True,
                         default="Detalhes simulados do pedido")

    order_date = Column(DateTime(timezone=True),
                        nullable=False, default=func.now())

    order = relationship('Client', back_populates="client_orders")
    product = relationship('Product', back_populates="product_orders")
