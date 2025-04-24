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
POSITION_URL = "https://api.n2yo.com/rest/v1/satellite/positions"

LAT = 0    # Equator
LON = 0    # Prime Meridian
ALT = 500  # km altitude
SECONDS = 1  # Only need 1 position

# Constants
EARTH_RADIUS = 6371  # km
MOON_DISTANCE = 384400  # km (average)

def fetch_satellites():
    """Fetch 20 unique satellites for each category stored in MongoDB and update their positions."""

    logging.info("Starting to fetch satellites...")
    
    # Get all satellites already fetched by category
    satellites = list(satellites_collection.find({}, {"_id": 0, "satellite_id": 1, "category_id": 1, "category_name": 1, "name": 1}))

    if not satellites:
        logging.error("❌ No satellites found in the database. Run your category fetcher first.")
        return

    logging.info(f"Found {len(satellites)} satellites to process.")

    updated_count = 0

    for sat in satellites:
        satid = sat["satellite_id"]
        satname = sat["name"]
        category_id = sat["category_id"]
        category_name = sat["category_name"]

        url = f"{POSITION_URL}/{satid}/{LAT}/{LON}/{ALT}/{SECONDS}/?apiKey={API_KEY}"
        logging.info(f"Fetching position for {satname} (ID: {satid}) - URL: {url}")
        
        try:
            response = requests.get(url)
            if response.status_code != 200:
                logging.warning(f"Failed to fetch satellite {satname}, status code: {response.status_code}")
                continue

            data = response.json()
            positions = data.get("positions", [])
            if not positions:
                logging.warning(f"No position data for satellite {satname}")
                continue

            position = positions[0]
            satlat = position.get("satlatitude", None)
            satlon = position.get("satlongitude", None)
            satalt = position.get("sataltitude", 0)

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

            updated_count += 1
            logging.info(f"✅ Updated {satname} (ID: {satid})")

        except Exception as e:
            logging.error(f"Error while processing satellite {satname}: {e}")
            continue

    logging.info(f"🎉 Satellite positions updated successfully. Total updated: {updated_count}")

if __name__ == "__main__":
    logging.info("Fetching satellite positions after delay...")
    fetch_satellites()
