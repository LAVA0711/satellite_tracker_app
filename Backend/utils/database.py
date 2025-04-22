import os
import logging
from dotenv import load_dotenv
from pymongo import MongoClient

# Load environment variables
load_dotenv()

logging.basicConfig(level=logging.INFO)

# Get MongoDB URI and Database Name from .env
MONGO_URI = os.getenv("MONGO_URI")
DATABASE_NAME = os.getenv("DATABASE_NAME")

# Connect to MongoDB
try:
    client = MongoClient(MONGO_URI)
    db = client[DATABASE_NAME]
    logging.info("✅ Connected to MongoDB successfully!")
except Exception as e:
    logging.error(f"❌ Failed to connect to MongoDB: {e}")

# Export the database instance
def get_db():
    return db
