from fastapi import APIRouter, Query
from typing import List
from order_service.models import (
    OrderCreate,
    OrderResponse,
    OrderUpdateStatus,
    OrderUpdateUserInfo,
)
from order_service import order_service

router = APIRouter()


@router.post("", response_model=OrderResponse, status_code=201)
def create_order(order: OrderCreate):
    order_doc = order_service.create_order(order)
    return OrderResponse(**order_doc)


@router.get("", response_model=List[OrderResponse])
def get_orders_by_status(status: str = Query(..., description="Order status filter")):
    orders = order_service.get_orders_by_status(status)
    return [OrderResponse(**order) for order in orders]


@router.put("/{order_id}/status", response_model=OrderResponse)
def update_order_status(order_id: str, status_update: OrderUpdateStatus):
    updated_order = order_service.update_order_status(order_id, status_update)
    return OrderResponse(**updated_order)


@router.put("/{order_id}/user-info", response_model=OrderResponse)
def update_order_user_info(order_id: str, user_info_update: OrderUpdateUserInfo):
    updated_order = order_service.update_order_user_info(order_id, user_info_update)
    return OrderResponse(**updated_order)


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(order_id: str):
    order = order_service.get_order(order_id)
    return OrderResponse(**order)

@router.get("/user/{user_account_id}", response_model=List[OrderResponse])
def get_orders_by_user(user_account_id: str):
    orders = order_service.get_orders_by_user_id(user_account_id)
    return [OrderResponse(**order) for order in orders]
