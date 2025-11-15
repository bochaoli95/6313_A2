from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Literal
from datetime import datetime

OrderStatus = Literal["under process", "shipping", "delivered"]

class OrderItem(BaseModel):
    item_id: str
    item_name: str
    quantity: int
    price: float

class OrderCreate(BaseModel):
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
    email: str
    delivery_address: str
    items: List[OrderItem]
    status: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    user_account_id: Optional[str] = None

class OrderResponse(BaseModel):
    order_id: str
    email: str
    delivery_address: str
    items: List[OrderItem]
    status: str
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
