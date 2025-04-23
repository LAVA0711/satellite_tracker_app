import requests
from pymongo import MongoClient
from Backend.utils.config import Config 
import time

# Connect to MongoDB
client = MongoClient(Config.MONGO_URI)
db = client.satellite_tracker  # Database name
categories_collection = db.categories  # Categories collection
satellites_collection = db.satellites  # Satellites collection

API_KEY = "9WXVRS-SEVLST-3BVGC5-5FKY"  # Replace with your valid API key
BASE_URL = "https://api.n2yo.com/rest/v1/satellite/above"

LAT = 0    # Equator
LON = 0    # Prime Meridian
ALT = 500  # 500 km altitude
RADIUS = 90  # Search radius

# Constants
EARTH_RADIUS = 6371  # km
MOON_DISTANCE = 384400  # km (average)

def fetch_satellites():
    """Fetch 20 unique satellites for each category stored in MongoDB and store them in the database."""
    
    # Retrieve all categories from MongoDB
    categories = list(categories_collection.find({}, {"_id": 0, "category_id": 1, "name": 1}))

    if not categories:
        print("❌ No categories found in the database. Run 'fetch_types.py' first.")
        return
    
    total_satellites = 0  # Track total satellites stored

    for category in categories:
        category_name = category["name"]
        category_id = category["category_id"]

        url = f"{BASE_URL}/{LAT}/{LON}/{ALT}/{RADIUS}/{category_id}/?apiKey={API_KEY}"
        response = requests.get(url)

        # Check if response is valid
        if response.status_code != 200:
            continue  # Skip category if request fails

        try:
            data = response.json()
        except ValueError:
            continue  # Skip if JSON is invalid

        # Ensure 'above' key exists in response
        if not data or "above" not in data:
            continue

        satellites = data["above"][:20]  # Get only the first 20 satellites
        total_satellites += len(satellites)

        for sat in satellites:
            # Ensure 'satid' (NORAD ID) exists and is valid
            satid = sat.get("satid")  # NORAD ID
            if not satid or not isinstance(satid, int):
                continue

            satname = sat.get("satname", "Unknown")  # Satellite Name
            satlat = sat.get("satlatitude", None)  # Latitude
            satlon = sat.get("satlongitude", None)  # Longitude
            satalt = sat.get("sataltitude", 0)  # Altitude (default 0 if missing)

            # Calculate distances
            distance_from_earth = EARTH_RADIUS + satalt  # Earth Radius + Altitude
            distance_from_moon = MOON_DISTANCE - distance_from_earth  # Moon Distance - Distance from Earth

            satellite_data = {
                "satellite_id": satid,  # Use correct field name
                "name": satname,
                "latitude": satlat,
                "longitude": satlon,
                "altitude": satalt,
                "distance_from_earth": distance_from_earth,
                "distance_from_moon": distance_from_moon,
                "category_name": category_name,
                "category_id": category_id
            }

            # Insert/update in MongoDB (ensures uniqueness using 'satellite_id')
            satellites_collection.update_one(
                {"satellite_id": satid}, {"$set": satellite_data}, upsert=True
            )

    print(f"✅ Satellites data updated successfully! Total satellites stored: {total_satellites}")

if __name__ == "__main__":
    while True:
        fetch_satellites()
        time.sleep(30)