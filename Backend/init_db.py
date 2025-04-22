from utils.database import db
from pymongo.errors import CollectionInvalid, DuplicateKeyError

def initialize_db():
    """Create MongoDB collections and ensure indexes are set properly."""
    
    # Create collections only if they don't exist
    try:
        db.create_collection("categories", check_exists=True)
    except CollectionInvalid:
        print("Collection 'categories' already exists.")
        
    try:
        db.create_collection("satellites", check_exists=True)
    except CollectionInvalid:
        print("Collection 'satellites' already exists.")
    
    # Clean up documents with None for satellite_id
    db.categories.delete_many({"satellite_id": None})

    # Ensure unique index on satellite_id in both collections
    try:
        db.categories.create_index("satellite_id", unique=True)
        print("✅ Unique index created on 'satellite_id' for categories collection.")
    except DuplicateKeyError as e:
        print(f"❌ Index creation failed: {e}")
    
    try:
        db.satellites.create_index("satellite_id", unique=True)
        print("✅ Unique index created on 'satellite_id' for satellites collection.")
    except DuplicateKeyError as e:
        print(f"❌ Index creation failed: {e}")

    print("✅ Database initialized successfully!")

if __name__ == "__main__":
    initialize_db()
