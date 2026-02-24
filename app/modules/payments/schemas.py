from pydantic import BaseModel
from datetime import datetime


class OrderItemResponse(BaseModel):
    id: int
    product_id: int
    product_name: str
    product_price: float
    quantity: int
    subtotal: float  # calculated: price * quantity

    class Config:
        from_attributes = True


class OrderResponse(BaseModel):
    id: int
    total_price: float
    status: str
    items: list[OrderItemResponse]
    created_at: datetime

    class Config:
        from_attributes = True


class CheckoutResponse(BaseModel):
    order_id: int
    status: str
    payment_url: str  # URL to redirect user for payment
    message: str