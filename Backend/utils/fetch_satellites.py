import requests
from pymongo import MongoClient
from Backend.utils.config import Config 
import time
import logging

# Logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# MongoDB setup
client = MongoClient(Config.MONGO_URI)
db = client.satellite_tracker
categories_collection = db.categories
satellites_collection = db.satellites

API_KEY = "9WXVRS-SEVLST-3BVGC5-5FKY"
BASE_URL = "https://api.n2yo.com/rest/v1/satellite/above"

ALT = 500    # Altitude
RADIUS = 90  # Radius of visibility

EARTH_RADIUS = 6371  # km
MOON_DISTANCE = 384400  # km (average)

# 🌍 Global coordinates to cover all Earth regions
GLOBAL_COORDINATES = [
    (0, 0), (45, 0), (-45, 0),
    (0, 90), (0, -90), (45, 90), (-45, -90),
    (60, 180), (-60, -180), (30, 60), (-30, -60)
]

def fetch_satellites():
    logging.info("🌍 Starting global satellite fetch...")

    categories = list(categories_collection.find({}, {"_id": 0, "category_id": 1, "name": 1}))
    if not categories:
        logging.error("❌ No categories found. Run 'fetch_types.py' first.")
        return

    total_satellites = 0

    for category in categories:
        category_id = category["category_id"]
        category_name = category["name"]

        satellite_map = {}
        logging.info(f"📡 Category: {category_name} (ID: {category_id})")

        for lat, lon in GLOBAL_COORDINATES:
            url = f"{BASE_URL}/{lat}/{lon}/{ALT}/{RADIUS}/{category_id}/?apiKey={API_KEY}"
            logging.info(f"🌐 Requesting: {url}")
            response = requests.get(url)

            if response.status_code != 200:
                logging.warning(f"⚠️ Failed for {lat},{lon} - Status code: {response.status_code}")
                continue

            try:
                data = response.json()
                satellites = data.get("above", [])
            except Exception as e:
                logging.error(f"❌ JSON parse error: {e}")
                continue

            for sat in satellites:
                satid = sat.get("satid")
                if satid and satid not in satellite_map:
                    satellite_map[satid] = sat
                if len(satellite_map) >= 50:
                    break
            if len(satellite_map) >= 50:
                break

        # Insert into MongoDB
        for satid, sat in satellite_map.items():
            satname = sat.get("satname", "Unknown")
            satlat = sat.get("satlatitude")
            satlon = sat.get("satlongitude")
            satalt = sat.get("sataltitude", 0)

            distance_from_earth = EARTH_RADIUS + satalt
            distance_from_moon = MOON_DISTANCE - distance_from_earth

            satellite_data = {
                "satellite_id": satid,
                "name": satname,
                "latitude": satlat,
                "longitude": satlon,
                "altitude": satalt,
                "distance_from_earth": distance_from_earth,
                "distance_from_moon": distance_from_moon,
                "category_name": category_name,
                "category_id": category_id
            }

            satellites_collection.update_one(
                {"satellite_id": satid}, {"$set": satellite_data}, upsert=True
            )
            logging.info(f"✅ Updated {satname} (ID: {satid})")

        total_satellites += len(satellite_map)
        logging.info(f"🛰️ Stored {len(satellite_map)} satellites for {category_name}")

    logging.info(f"🚀 Finished updating. Total satellites inserted: {total_satellites}")

if __name__ == "__main__":
    fetch_satellites()
