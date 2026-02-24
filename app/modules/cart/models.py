from sqlalchemy import String, Integer, ForeignKey, Column
from app.core.database import Base
from sqlalchemy.orm import relationship

class Cart(Base):
    __tablename__="carts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    
    items = relationship("CartItem", back_populates="cart")

class CartItem(Base):
    __tablename__="cart_items"

    id = Column(Integer, primary_key=True, index=True)
    cart_id = Column(Integer, ForeignKey("carts.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)

    cart = relationship("Cart", back_populates="items")
    product = relationship("Product")