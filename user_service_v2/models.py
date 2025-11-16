from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class BaseUserModel(BaseModel):
    version: int = Field(default=1, description="Version number, increments with each update")

    class Config:
        orm_mode = True


class UserInDB(BaseUserModel):
    user_account_id: str = Field(..., description="Unique user account ID")
    email: EmailStr = Field(..., description="User email address")
    delivery_address: str = Field(..., description="User delivery address")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="User creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "user_account_id": "U12345",
                "email": "user@example.com",
                "delivery_address": "1234 Boulevard René-Lévesque, Montréal, QC",
                "created_at": "2025-11-15T12:00:00Z",
                "updated_at": "2025-11-15T12:00:00Z",
                "version": 1
            }
        }


class UserCreate(BaseUserModel):
    user_account_id: str = Field(..., example="U10001", description="Unique ID for user account")
    email: EmailStr = Field(..., example="jane.doe@example.com", description="User's email address")
    delivery_address: str = Field(..., example="555 Sherbrooke St W, Montréal, QC", description="Delivery address")

    class Config:
        schema_extra = {
            "example": {
                "user_account_id": "U10001",
                "email": "jane.doe@example.com",
                "delivery_address": "555 Sherbrooke St W, Montréal, QC",
                "version": 1
            }
        }


class UserUpdate(BaseUserModel):
    email: Optional[EmailStr] = Field(None, example="new.email@example.com", description="New email address")
    delivery_address: Optional[str] = Field(
        None,
        example="6789 Rue Sainte-Catherine, Montréal, QC",
        description="New delivery address"
    )

    class Config:
        schema_extra = {
            "example": {
                "email": "new.email@example.com",
                "delivery_address": "6789 Rue Sainte-Catherine, Montréal, QC",
                "version": 2
            }
        }


class UserResponse(BaseUserModel):
    user_account_id: str = Field(..., description="User account ID")
    email: str = Field(..., description="User email")
    delivery_address: str = Field(..., description="User delivery address")
    created_at: Optional[datetime] = Field(None, description="User creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "user_account_id": "U10001",
                "email": "jane.doe@example.com",
                "delivery_address": "555 Sherbrooke St W, Montréal, QC",
                "created_at": "2025-11-15T12:00:00Z",
                "updated_at": "2025-11-15T12:10:00Z",
                "version": 2
            }
        }
