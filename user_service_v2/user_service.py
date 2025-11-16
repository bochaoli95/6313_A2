from datetime import datetime
from fastapi import HTTPException, status
from common.database import user_db_connection
from common.event_publisher import event_publisher
from user_service_v2.models import UserCreate, UserUpdate, UserInDB


def create_user(user: UserCreate) -> dict:
    db = user_db_connection.get_database_sync()
    collection = db.users

    existing_user = collection.find_one({"user_account_id": user.user_account_id})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this account ID already exists"
        )

    user_in_db = UserInDB(
        user_account_id=user.user_account_id,
        email=user.email,
        delivery_address=user.delivery_address,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        version=1
    )

    result = collection.insert_one(user_in_db.dict())
    if not result.inserted_id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )

    return user_in_db.dict()


def update_user(user_account_id: str, user_update: UserUpdate) -> dict:
    db = user_db_connection.get_database_sync()
    collection = db.users

    user = collection.find_one({"user_account_id": user_account_id})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    update_fields = {}
    if user_update.email is not None:
        update_fields["email"] = user_update.email
    if user_update.delivery_address is not None:
        update_fields["delivery_address"] = user_update.delivery_address

    if not update_fields:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update"
        )

    update_fields["updated_at"] = datetime.utcnow()
    update_fields["version"] = user.get("version", 1) + 1

    result = collection.update_one(
        {"user_account_id": user_account_id},
        {"$set": update_fields}
    )

    if result.modified_count == 0:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user"
        )

    updated_user = collection.find_one({"user_account_id": user_account_id})

    event_publisher.publish_user_update_event(
        user_id=updated_user["user_account_id"],
        email=updated_user["email"],
        delivery_address=updated_user["delivery_address"]
    )

    return updated_user


def get_user(user_account_id: str) -> dict:
    db = user_db_connection.get_database_sync()
    collection = db.users

    user = collection.find_one({"user_account_id": user_account_id})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return user
