from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from pymongo.collection import Collection
from math import radians, cos, sin, asin, sqrt
from Backend.utils.database import get_db  # ensure this is correctly set up

app = FastAPI()

# 🌍 Allow CORS (important for frontend communication, e.g., Flutter)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to specific domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Root route to test if server is alive (useful for Render or Vercel)
@app.get("/")
def root():
    return {"message": "FastAPI backend is running!"}

# 📏 Haversine formula to calculate distance between two coordinates
def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371  # Earth radius in km
    d_lat = radians(lat2 - lat1)
    d_lon = radians(lon2 - lon1)
    a = sin(d_lat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(d_lon / 2) ** 2
    c = 2 * asin(sqrt(a))
    return R * c

# 🚀 Route: Get satellites above a location
@app.get("/satellites/above")
def get_satellites_above(
    lat: float = Query(..., description="Latitude of the location"),
    lon: float = Query(..., description="Longitude of the location"),
    radius_km: float = Query(100, description="Search radius in kilometers")
):
    db = get_db()
    satellites_collection: Collection = db.satellites

    satellites = list(satellites_collection.find({}, {"_id": 0}))
    filtered_satellites = []

    for sat in satellites:
        sat_lat = sat.get("latitude")
        sat_lon = sat.get("longitude")

        if sat_lat is None or sat_lon is None:
            continue

        distance = haversine(lat, lon, sat_lat, sat_lon)
        if distance <= radius_km:
            filtered_satellites.append(sat)

    return {
        "count": len(filtered_satellites),
        "satellites": filtered_satellites
    }

# 📚 Route: Get all satellite types (categories)
@app.get("/satellite-types")
def get_satellite_types():
    db = get_db()
    categories_collection: Collection = db.categories
    categories = list(categories_collection.find({}, {"_id": 0}))

    if not categories:
        raise HTTPException(status_code=404, detail="No satellite categories found.")

    return {"categories": categories}

# 🔍 Route: Get satellites by category ID
@app.get("/satellites/by-category/{category_id}")
def get_satellites_by_category(category_id: int):
    db = get_db()
    satellites_collection: Collection = db.satellites
    satellites = list(satellites_collection.find({"category_id": category_id}, {"_id": 0}))

    if not satellites:
        raise HTTPException(status_code=404, detail=f"No satellites found for category ID {category_id}.")

    return {
        "count": len(satellites),
        "satellites": satellites
    }
