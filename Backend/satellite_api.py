from fastapi import APIRouter
from utils.database import get_db
from pymongo.collection import Collection

satellite_router = APIRouter()

@satellite_router.get("/satellites/types")
def get_satellite_types():
    db = get_db()
    categories_collection: Collection = db.categories

    categories = list(categories_collection.find({}, {"_id": 0}))
    return categories

@satellite_router.get("/satellites/category/{category_name}")
def get_satellites_by_category(category_name: str):
    db = get_db()
    satellites_collection: Collection = db.satellites

    satellites = list(satellites_collection.find({"category_name": category_name}, {"_id": 0}))
    return satellites
