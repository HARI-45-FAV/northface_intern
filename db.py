import os
import sys
from pymongo import MongoClient
from dotenv import load_dotenv
from urllib.parse import quote_plus  # <-- Import this

load_dotenv()

# --- Load components from .env ---
MONGO_USER = os.getenv("MONGO_USER")
MONGO_PASS = os.getenv("MONGO_PASS")
MONGO_CLUSTER = os.getenv("MONGO_CLUSTER")
DB_NAME = "hrms_db"

# --- Escape username and password ---
if not all([MONGO_USER, MONGO_PASS, MONGO_CLUSTER]):
    print("FATAL: Missing MongoDB environment variables (MONGO_USER, MONGO_PASS, MONGO_CLUSTER).")
    sys.exit(1)

MONGO_URI = f"mongodb+srv://{quote_plus(MONGO_USER)}:{quote_plus(MONGO_PASS)}@{MONGO_CLUSTER}/?retryWrites=true&w=majority"

def get_db_connection():
    try:
        # --- Use the constructed URI ---
        client = MongoClient(MONGO_URI)
        client.admin.command('ping')
        print("✅ Successfully connected to MongoDB!")
        return client[DB_NAME]
    except Exception as e:
        print(f"❌ Could not connect to MongoDB. Error: {e}")
        return None

db = get_db_connection()

if db is not None:
    users_col = db["users"]
    attendance_col = db["attendance"]
    leaves_col = db["leaves"]
    announcements_col = db["announcements"]
    chats_col = db["chats"]
else:
    print("FATAL: Database connection failed. The application cannot start.")
    sys.exit(1)