import os
import json
import pika
import threading
import time
from datetime import datetime
from common.database import order_db_connection
from dotenv import load_dotenv

base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
env_path = os.path.join(base_dir, ".env")
load_dotenv(env_path)


class EventConsumer:
    def __init__(self):
        self.host = os.getenv("RABBITMQ_HOST")
        self.port = int(os.getenv("RABBITMQ_PORT"))
        self.username = os.getenv("RABBITMQ_USERNAME")
        self.password = os.getenv("RABBITMQ_PASSWORD")
        self.exchange = os.getenv("RABBITMQ_EXCHANGE")
        self.queue = os.getenv("RABBITMQ_QUEUE")
        self.routing_key = "user.updated"

    def connect(self):
        credentials = pika.PlainCredentials(self.username, self.password)
        params = pika.ConnectionParameters(
            host=self.host,
            port=self.port,
            credentials=credentials,
            heartbeat=600,
            blocked_connection_timeout=300,
        )
        connection = pika.BlockingConnection(params)
        channel = connection.channel()
        channel.exchange_declare(exchange=self.exchange, exchange_type="topic", durable=True)
        channel.queue_declare(queue=self.queue, durable=True)
        channel.queue_bind(exchange=self.exchange, queue=self.queue, routing_key=self.routing_key)
        return connection, channel

    def sync_user_info(self, user_id: str, email: str = None, delivery_address: str = None):
        db = order_db_connection.get_database_sync()
        collection = db.orders
        update_fields = {}
        if email:
            update_fields["email"] = email
        if delivery_address:
            update_fields["delivery_address"] = delivery_address
        if not update_fields:
            return
        update_fields["updated_at"] = datetime.utcnow()
        result = collection.update_many({"user_account_id": user_id}, {"$set": update_fields})
        print(f"[Consumer] Synced {result.modified_count} orders for user {user_id}")

    def start(self):
        def consume():
            while True:
                try:
                    connection, channel = self.connect()
                    print(f"[Consumer] Listening for '{self.routing_key}' events...")
                    for method, properties, body in channel.consume(self.queue, inactivity_timeout=5):
                        if not body:
                            continue
                        try:
                            event = json.loads(body)
                            if event.get("event_type") == self.routing_key:
                                self.sync_user_info(
                                    event.get("user_id"),
                                    event.get("email"),
                                    event.get("delivery_address"),
                                )
                            channel.basic_ack(method.delivery_tag)
                        except Exception as e:
                            print(f"[Consumer] Error processing event: {e}")
                            channel.basic_nack(method.delivery_tag, requeue=True)
                except Exception as e:
                    print(f"[Consumer] Connection error: {e}, retrying in 5s...")
                    time.sleep(5)

        thread = threading.Thread(target=consume, daemon=True)
        thread.start()


event_consumer = EventConsumer()
