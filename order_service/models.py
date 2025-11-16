from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Literal
from datetime import datetime

# Allowed order status
OrderStatus = Literal["under process", "shipping", "delivered"]


class OrderItem(BaseModel):
    item_id: str
    item_name: str
    quantity: int
    price: float


class OrderCreate(BaseModel):
    user_account_id: str
    email: EmailStr
    delivery_address: str
    items: List[OrderItem]


class OrderUpdateStatus(BaseModel):
    status: OrderStatus


class OrderUpdateUserInfo(BaseModel):
    email: Optional[EmailStr] = None
    delivery_address: Optional[str] = None


class OrderInDB(BaseModel):
    order_id: str
    user_account_id: str
    email: str
    delivery_address: str
    items: List[OrderItem]
    status: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class OrderResponse(BaseModel):
    order_id: str
    user_account_id: str
    email: str
    delivery_address: str
    items: List[OrderItem]
    status: str
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
