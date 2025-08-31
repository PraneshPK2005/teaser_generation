from pymongo import MongoClient
import os
from datetime import datetime

# MongoDB setup
client = MongoClient(os.getenv("MONGO_URI"))
db = client["teaser_app"]

# Existing collection for users
users_collection = db["users"]

# New collection for storing user teaser history
user_history_collection = db["user_teaser_history"]
