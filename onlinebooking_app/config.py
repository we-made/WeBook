import os
from dotenv import load_dotenv

load_dotenv()

APP_TITLE = os.getenv("APP_TITLE", "WeBook - Online Booking System")
APP_DESCRIPTION = os.getenv("APP_DESCRIPTION", "A simple online booking system")

SERVICE_ACCOUNT_USERNAME = os.getenv("SERVICE_ACCOUNT_USERNAME", "service_account")
SERVICE_ACCOUNT_PASSWORD = os.getenv("SERVICE_ACCOUNT_PASSWORD", "password")

API_URL = os.getenv("API_URL", "http://localhost:8000/api")
