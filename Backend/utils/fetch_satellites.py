import requests
from pymongo import MongoClient
from Backend.utils.config import Config 
import logging

# Logging config
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# MongoDB
client = MongoClient(Config.MONGO_URI)
db = client.satellite_tracker
categories_collection = db.categories
satellites_collection = db.satellites

API_KEY = "9WXVRS-SEVLST-3BVGC5-5FKY"
BASE_URL = "https://api.n2yo.com/rest/v1/satellite/above"

EARTH_RADIUS = 6371
MOON_DISTANCE = 384400

ALT = 500
RADIUS = 90

GLOBAL_COORDINATES = [
    (0, 0), (45, 0), (-45, 0),
    (0, 90), (0, -90), (45, 90), (-45, -90),
    (60, 180), (-60, -180), (30, 60), (-30, -60)
]

def fetch_satellites():
    logging.info("🌍 Fetching top 25 satellites per category globally...")

    categories = list(categories_collection.find({}, {"_id": 0, "category_id": 1, "name": 1}))
    if not categories:
        logging.error("❌ No categories found. Run 'fetch_types.py' first.")
        return

    total_inserted = 0

    for category in categories:
        category_id = category["category_id"]
        category_name = category["name"]
        logging.info(f"\n📡 Category: {category_name} (ID: {category_id})")

        satellite_map = {}

        for lat, lon in GLOBAL_COORDINATES:
            url = f"{BASE_URL}/{lat}/{lon}/{ALT}/{RADIUS}/{category_id}/?apiKey={API_KEY}"
            try:
                response = requests.get(url)
                if response.status_code != 200:
                    continue

                satellites = response.json().get("above", [])
                for sat in satellites:
                    satid = sat.get("satid")
                    if satid and satid not in satellite_map:
                        satellite_map[satid] = sat
                    if len(satellite_map) >= 25:
                        break
            except Exception as e:
                logging.warning(f"⚠️ Error fetching/parsing data: {e}")
                continue
            if len(satellite_map) >= 25:
                break

        for satid, sat in satellite_map.items():
            satname = sat.get("satname", "Unknown")
            satlat = sat.get("satlat")
            satlon = sat.get("satlng")
            satalt = sat.get("satalt", 0)

            if satlat is None or satlon is None:
                continue

            satellite_data = {
                "satellite_id": satid,
                "name": satname,
                "latitude": satlat,
                "longitude": satlon,
                "altitude": satalt,
                "distance_from_earth": EARTH_RADIUS + satalt,
                "distance_from_moon": MOON_DISTANCE - (EARTH_RADIUS + satalt),
                "category_name": category_name,
                "category_id": category_id
            }

            satellites_collection.update_one(
                {"satellite_id": satid},
                {"$set": satellite_data},
                upsert=True
            )
            logging.info(f"✅ Inserted: {satname} (ID: {satid})")

        total_inserted += len(satellite_map)

    logging.info(f"\n🚀 Done. Total satellites inserted: {total_inserted}")

if __name__ == "__main__":
    fetch_satellites()
