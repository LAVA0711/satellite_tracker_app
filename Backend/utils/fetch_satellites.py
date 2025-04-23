import requests
from pymongo import MongoClient
from Backend.utils.config import Config 
import time
import logging

# Set up logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Connect to MongoDB
client = MongoClient(Config.MONGO_URI)
db = client.satellite_tracker  # Database name
categories_collection = db.categories  # Categories collection
satellites_collection = db.satellites  # Satellites collection

API_KEY = "9WXVRS-SEVLST-3BVGC5-5FKY"  # Replace with your valid API key
BASE_URL = "https://api.n2yo.com/rest/v1/satellite/positions"

LAT = 0    # Equator
LON = 0    # Prime Meridian
ALT = 500  # 500 km altitude
RADIUS = 90  # Search radius

# Constants
EARTH_RADIUS = 6371  # km
MOON_DISTANCE = 384400  # km (average)

def fetch_satellites():
    """Fetch 20 unique satellites for each category stored in MongoDB and store them in the database."""
    
    logging.info("Starting to fetch satellites...")
    
    # Retrieve all categories from MongoDB
    categories = list(categories_collection.find({}, {"_id": 0, "category_id": 1, "name": 1}))

    if not categories:
        logging.error("❌ No categories found in the database. Run 'fetch_types.py' first.")
        return
    
    total_satellites = 0  # Track total satellites stored
    logging.info(f"Found {len(categories)} categories to process.")

    for category in categories:
        category_name = category["name"]
        category_id = category["category_id"]

        url = f"{BASE_URL}/{LAT}/{LON}/{ALT}/{RADIUS}/{category_id}/?apiKey={API_KEY}"
        logging.info(f"Fetching category: {category_name}, ID: {category_id} - URL: {url}")
        response = requests.get(url)

        # Check if response is valid
        if response.status_code != 200:
            logging.warning(f"Failed to fetch data for category {category_name}, status code: {response.status_code}")
            continue  # Skip category if request fails

        try:
            data = response.json()
        except ValueError:
            logging.error(f"Failed to parse JSON for category {category_name}")
            continue  # Skip if JSON is invalid

        if not data or "above" not in data:
            logging.warning(f"No satellites data in response for category {category_name}")
            continue

        satellites = data["above"][:20]  # Get only the first 20 satellites
        total_satellites += len(satellites)

        logging.info(f"Found {len(satellites)} satellites for category {category_name}")

        for sat in satellites:
            satid = sat.get("satid")
            if not satid or not isinstance(satid, int):
                continue

            satname = sat.get("satname", "Unknown")
            satlat = sat.get("satlatitude", None)
            satlon = sat.get("satlongitude", None)
            satalt = sat.get("sataltitude", 0)

            # Calculate distances
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
            logging.info(f"Satellite {satname} (ID: {satid}) added/updated in MongoDB.")

    logging.info(f"✅ Satellites data updated successfully! Total satellites stored: {total_satellites}")

if __name__ == "__main__":
    logging.info("Fetching satellites...")
    time.sleep(30)  # Simulate initial delay if needed
    logging.info("Done fetching.")
    fetch_satellites()
