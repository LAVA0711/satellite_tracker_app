import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
from utils.config import Config

# Connect to MongoDB
client = MongoClient(Config.MONGO_URI)
db = client.satellite_tracker
categories_collection = db.categories

def get_categories():
    url = "https://www.n2yo.com/satellites/"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        return {}

    soup = BeautifulSoup(response.text, "html.parser")
    categories = {}
    rows = soup.find_all("tr")

    for row in rows:
        cols = row.find_all("td")
        if len(cols) > 1:
            category_link = cols[0].find("a")
            if category_link and "?c=" in category_link["href"]:
                cat_id = category_link["href"].split("=")[-1]
                cat_name = category_link.text.strip()
                
                if cat_id.isdigit():
                    cat_id = int(cat_id)
                    categories[cat_name] = cat_id

                    categories_collection.update_one(
                        {"category_id": cat_id},
                        {"$set": {"name": cat_name, "category_id": cat_id}},
                        upsert=True
                    )

    return categories

if __name__ == "__main__":
    get_categories()
