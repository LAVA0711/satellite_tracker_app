from dotenv import load_dotenv, find_dotenv
import os
class Config:
    # Find the .env file path manually
    env_path = "C:/Users/DELL/StudioProjects/Satellite_Tracker_App/Backend/utils/.env"

    # Load environment variables from the explicitly given .env file
    load_dotenv(dotenv_path=env_path)

    # Safely fetch values from .env
    MONGO_URI = os.getenv("MONGO_URI", "").strip()
    DATABASE_NAME = os.getenv("DATABASE_NAME", "").strip()
    N2YO_API_KEY = os.getenv("N2YO_API_KEY", "").strip()
