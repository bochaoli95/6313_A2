# user_service_v1/routes/user_routes.py
from fastapi import APIRouter
from user_service_v2.models import UserCreate, UserUpdate, UserResponse
from user_service_v2 import user_service

router = APIRouter()


@router.post("", response_model=UserResponse, status_code=201)
def create_user(user: UserCreate):
    created_user = user_service.create_user(user)
    return UserResponse(**created_user)


@router.put("/{user_account_id}", response_model=UserResponse)
def update_user(user_account_id: str, user_update: UserUpdate):
    updated_user = user_service.update_user(user_account_id, user_update)
    return UserResponse(**updated_user)


@router.get("/{user_account_id}", response_model=UserResponse)
def get_user(user_account_id: str):
    user = user_service.get_user(user_account_id)
    return UserResponse(**user)
