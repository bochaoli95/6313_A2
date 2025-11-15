import pika
import json
import os
import time
from dotenv import load_dotenv

base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
env_path = os.path.join(base_dir, ".env")
load_dotenv(env_path)

class EventPublisher:
    def __init__(self):
        self.host = os.getenv("RABBITMQ_HOST")
        self.port = int(os.getenv("RABBITMQ_PORT"))
        self.username = os.getenv("RABBITMQ_USERNAME")
        self.password = os.getenv("RABBITMQ_PASSWORD")
        self.exchange = os.getenv("RABBITMQ_EXCHANGE")
        self.queue = os.getenv("RABBITMQ_QUEUE")
        self.routing_key = "user.updated"
        self.connection = None
        self.channel = None

    def connect(self):
        while True:
            try:
                credentials = pika.PlainCredentials(self.username, self.password)
                parameters = pika.ConnectionParameters(
                    host=self.host,
                    port=self.port,
                    credentials=credentials,
                    heartbeat=600,
                    blocked_connection_timeout=300,
                )
                self.connection = pika.BlockingConnection(parameters)
                self.channel = self.connection.channel()
                self.channel.exchange_declare(exchange=self.exchange, exchange_type="topic", durable=True)
                self.channel.queue_declare(queue=self.queue, durable=True)
                self.channel.queue_bind(exchange=self.exchange, queue=self.queue, routing_key=self.routing_key)
                print(f"[Publisher] Connected to RabbitMQ at {self.host}:{self.port}")
                break
            except Exception as e:
                print(f"[Publisher] Connection failed: {e}, retrying in 5s...")
                time.sleep(5)

    def publish_user_update_event(self, user_id: str, email: str = None, delivery_address: str = None):
        event_data = {
            "event_type": self.routing_key,
            "user_id": user_id,
            "email": email,
            "delivery_address": delivery_address,
        }
        message = json.dumps(event_data)
        try:
            if not self.connection or self.connection.is_closed:
                self.connect()
            self.channel.basic_publish(
                exchange=self.exchange,
                routing_key=self.routing_key,
                body=message,
                properties=pika.BasicProperties(delivery_mode=2),
            )
            print(f"[Publisher] Sent event: {event_data}")
        except Exception as e:
            print(f"[Publisher] Publish failed: {e}, reconnecting...")
            self.connect()
            try:
                self.channel.basic_publish(
                    exchange=self.exchange,
                    routing_key=self.routing_key,
                    body=message,
                    properties=pika.BasicProperties(delivery_mode=2),
                )
            except Exception as err:
                print(f"[Publisher] Retry failed: {err}")

    def close(self):
        if self.connection and not self.connection.is_closed:
            self.connection.close()
            print("[Publisher] Connection closed")


event_publisher = EventPublisher()
