from pymongo import MongoClient
from utils.config import Config

client = MongoClient(Config.MONGO_URI)
db = client.satellite_tracker
categories_collection = db.categories

# List current indexes
print("Indexes before:")
print(list(categories_collection.list_indexes()))

# Drop the wrong index
categories_collection.drop_index("satellite_id_1")

print("❌ Dropped wrong index: satellite_id_1")

categories_collection.create_index("category_id", unique=True)
print("✅ Created correct unique index on category_id")
