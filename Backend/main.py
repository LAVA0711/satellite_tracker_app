from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from pymongo.collection import Collection
from math import radians, cos, sin, asin, sqrt
from utils.database import get_db

app = FastAPI()

# CORS for Flutter access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can restrict this later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Helper: Calculate distance using Haversine formula
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in km
    d_lat = radians(lat2 - lat1)
    d_lon = radians(lon2 - lon1)
    a = sin(d_lat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(d_lon/2)**2
    c = 2 * asin(sqrt(a))
    return R * c

# 🚀 Existing route: Get satellites above a location
@app.get("/satellites/above")
def get_satellites_above(lat: float = Query(...), lon: float = Query(...), radius_km: float = Query(100)):
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

# ✅ New route: Get all satellite types (categories)
@app.get("/satellite-types")
def get_satellite_types():
    db = get_db()
    categories_collection: Collection = db.categories
    categories = list(categories_collection.find({}, {"_id": 0}))
    return {"categories": categories}

# ✅ New route: Get satellites by category ID
@app.get("/satellites/by-category/{category_id}")
def get_satellites_by_category(category_id: int):
    db = get_db()
    satellites_collection: Collection = db.satellites
    satellites = list(satellites_collection.find({"category_id": category_id}, {"_id": 0}))
    return {
        "count": len(satellites),
        "satellites": satellites
    }
