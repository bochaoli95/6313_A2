from fastapi import FastAPI
from contextlib import asynccontextmanager
from common.database import order_db_connection
from common.event_consumer import event_consumer
from order_service.order_routes import router as order_router
import uvicorn
import os


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("[OrderService] Starting...")
    order_db_connection.connect_sync()
    event_consumer.start()
    yield
    order_db_connection.close_sync()
    print("[OrderService] Stopped.")


app = FastAPI(
    title="Order Microservice",
    description="Handles order management and syncs user updates via RabbitMQ",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(order_router, prefix="/orders", tags=["Orders"])


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8003))
    uvicorn.run(app, host="0.0.0.0", port=port)
