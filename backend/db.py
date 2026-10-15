import os
from pathlib import Path
from pymongo import MongoClient
from dotenv import load_dotenv

project_root = Path(__file__).resolve().parent.parent
load_dotenv(project_root / ".env")

MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    raise ValueError("MONGO_URI is missing. Check your .env file.")

client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)

db = client["ecommerce"]
products_collection = db["products"]

if __name__ == "__main__":
    try:
        client.admin.command("ping")
        print("Successfully connected to MongoDB Atlas!")
    except Exception as e:
        print("MongoDB connection failed:", e)