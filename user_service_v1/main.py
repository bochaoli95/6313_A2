"""
User Microservice v1
Handles user management: create users, update email and delivery address
Publishes events to RabbitMQ when user data is updated
"""
from fastapi import FastAPI
from contextlib import asynccontextmanager
from common.database import user_db_connection
from common.event_publisher import event_publisher
from user_service_v1.user_routes import router as user_router
import uvicorn
import os


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("[UserService v1] Starting...")
    user_db_connection.connect_sync()
    event_publisher.connect()
    yield
    event_publisher.close()
    user_db_connection.close_sync()
    print("[UserService v1] Stopped.")


app = FastAPI(
    title="User Microservice v1",
    description="User service v1 (publishes user update events)",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(user_router, prefix="/users", tags=["Users"])


@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "user-service-v1"}


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8001))
    uvicorn.run(app, host="0.0.0.0", port=port)
