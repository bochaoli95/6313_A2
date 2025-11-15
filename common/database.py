from pymongo import MongoClient
from typing import Optional
import os
from dotenv import load_dotenv

base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
env_path = os.path.join(base_dir, ".env")
load_dotenv(env_path)

class MongoDBConnection:
    def __init__(self, host: str, port: int, database: str, username: str = None, password: str = None):
        self.host = host
        self.port = port
        self.database_name = database
        self.username = username
        self.password = password
        self.sync_client: Optional[MongoClient] = None

    def connect_sync(self):
        if not self.sync_client:
            if self.username and self.password:
                connection_string = f"mongodb://{self.username}:{self.password}@{self.host}:{self.port}/"
            else:
                connection_string = f"mongodb://{self.host}:{self.port}/"
            self.sync_client = MongoClient(connection_string)
        return self.sync_client

    def get_database_sync(self):
        if not self.sync_client:
            self.connect_sync()
        return self.sync_client[self.database_name]

    def close_sync(self):
        if self.sync_client:
            self.sync_client.close()
            self.sync_client = None


# Global connection instances
user_db_connection = MongoDBConnection(
    host=os.getenv("MONGODB_HOST", "localhost"),
    port=int(os.getenv("MONGODB_PORT", 27017)),
    username=os.getenv("MONGODB_USERNAME"),
    password=os.getenv("MONGODB_PASSWORD"),
    database=os.getenv("USER_DB_NAME", "user_db")
)

order_db_connection = MongoDBConnection(
    host=os.getenv("MONGODB_HOST", "localhost"),
    port=int(os.getenv("MONGODB_PORT", 27017)),
    username=os.getenv("MONGODB_USERNAME"),
    password=os.getenv("MONGODB_PASSWORD"),
    database=os.getenv("ORDER_DB_NAME", "order_db")
)
