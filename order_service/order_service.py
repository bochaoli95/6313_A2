from datetime import datetime
from fastapi import HTTPException
from common.database import order_db_connection
from order_service.models import (
    OrderCreate,
    OrderUpdateStatus,
    OrderUpdateUserInfo,
    OrderInDB,
)
import uuid


def create_order(order: OrderCreate) -> dict:
    """
    Create a new order in MongoDB.
    Each order is tied to a user_account_id (used for synchronization).
    """
    db = order_db_connection.get_database_sync()
    collection = db.orders

    order_id = str(uuid.uuid4())

    order_in_db = OrderInDB(
        order_id=order_id,
        user_account_id=order.user_account_id,
        email=order.email,
        delivery_address=order.delivery_address,
        items=order.items,
        status="under process",
    )

    result = collection.insert_one(order_in_db.dict())
    if not result.inserted_id:
        raise HTTPException(status_code=500, detail="Failed to create order")

    return order_in_db.dict()


def get_orders_by_status(order_status: str) -> list:
    db = order_db_connection.get_database_sync()
    collection = db.orders

    orders = list(collection.find({"status": order_status}))
    return orders


def update_order_status(order_id: str, status_update: OrderUpdateStatus) -> dict:
    db = order_db_connection.get_database_sync()
    collection = db.orders

    order = collection.find_one({"order_id": order_id})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    result = collection.update_one(
        {"order_id": order_id},
        {"$set": {"status": status_update.status, "updated_at": datetime.utcnow()}},
    )

    if result.modified_count == 0:
        raise HTTPException(status_code=500, detail="Failed to update order status")

    return collection.find_one({"order_id": order_id})


def update_order_user_info(order_id: str, user_info_update: OrderUpdateUserInfo) -> dict:
    db = order_db_connection.get_database_sync()
    collection = db.orders

    order = collection.find_one({"order_id": order_id})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    update_fields = {}
    if user_info_update.email is not None:
        update_fields["email"] = user_info_update.email
    if user_info_update.delivery_address is not None:
        update_fields["delivery_address"] = user_info_update.delivery_address

    if not update_fields:
        raise HTTPException(status_code=400, detail="No fields to update")

    update_fields["updated_at"] = datetime.utcnow()

    result = collection.update_one(
        {"order_id": order_id}, {"$set": update_fields}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=500, detail="Failed to update user info")

    return collection.find_one({"order_id": order_id})


def get_order(order_id: str) -> dict:
    db = order_db_connection.get_database_sync()
    collection = db.orders

    order = collection.find_one({"order_id": order_id})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    return order


def get_orders_by_user_id(user_account_id: str) -> list:
    """
    Retrieve all orders for a specific user_account_id.
    """
    db = order_db_connection.get_database_sync()
    collection = db.orders

    orders = list(collection.find({"user_account_id": user_account_id}))

    if not orders:
        raise HTTPException(status_code=404, detail=f"No orders found for user {user_account_id}")

    return orders