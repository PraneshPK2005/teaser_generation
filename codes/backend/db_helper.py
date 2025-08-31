from datetime import datetime
from db import user_history_collection

def save_teaser_history(user_email, method, youtube_url, main_file_url, teaser_file_url, duration, extra_data=None):
    """
    Save or update a user's teaser generation history in MongoDB.
    Each user will have one document containing an array of 'teasers'.
    """
    if extra_data is None:
        extra_data = {}

    entry = {
        "method": method,
        "youtube_url": youtube_url,
        "main_file_url": main_file_url,
        "teaser_file_url": teaser_file_url,
        "duration": duration,
        "created_at": datetime.utcnow(),
        **extra_data
    }

    # Upsert document for user
    user_history_collection.update_one(
        {"email": user_email},
        {"$push": {"teasers": entry}, "$setOnInsert": {"email": user_email}},
        upsert=True
    )
