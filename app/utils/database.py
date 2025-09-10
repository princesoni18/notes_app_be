
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
load_dotenv()
import os

# MongoDB connection URL (set MONGODB_PASSWORD in your .env for security)
MONGODB_PASSWORD = os.getenv("MONGODB_PASSWORD", "")
MONGODB_URL = f"mongodb+srv://ps983309:{MONGODB_PASSWORD}@cluster0.5fwgxdg.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
MONGODB_DB = os.getenv("MONGODB_DB", "SOL")


class Database:
    client: AsyncIOMotorClient = None
    db = None

db_instance = Database()

async def connect_to_mongo():
    db_instance.client = AsyncIOMotorClient(MONGODB_URL)
    db_instance.db = db_instance.client[MONGODB_DB]

async def close_mongo_connection():
    if db_instance.client:
        db_instance.client.close()

async def get_db():
    return db_instance.db