import os
from pymongo import MongoClient, UpdateOne
from dotenv import load_dotenv

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI", "")
MONGODB_DB = os.getenv("MONGODB_DB", "file_hashes_db")
MONGODB_COLLECTION = os.getenv("MONGODB_COLLECTION", "hashes")


def get_mongo_collection():
    """Return MongoDB collection handle or None."""
    if not MONGODB_URI:
        print(" MONGODB_URI not set. Skipping DB operations.")
        return None
    try:
        client = MongoClient(MONGODB_URI)
        db = client[MONGODB_DB]
        collection = db[MONGODB_COLLECTION]
        collection.create_index("filename", unique=True)
        return collection
    except Exception as e:
        print(f"MongoDB connection failed: {e}")
        return None


def upsert_hashes(data):
    """Upsert (filename, hash) list into MongoDB."""
    col = get_mongo_collection()
    if col is None:  
        return
    try:
        ops = [
            UpdateOne(
                {"filename": fn},
                {"$set": {"filename": fn, "hash": digest, "recordId": new_record_Id}},
                upsert=True
            )
            for fn, digest, new_record_Id in data
        ]
        if not ops:
            return
        result = col.bulk_write(ops, ordered=False)
        return {
            "upserted": result.upserted_count,
            "modified": result.modified_count,
        }
    except Exception as e:
        print(f"Error writing to MongoDB: {e}")
        return None


def find_file_by_hash(file_hash):
    
    col = get_mongo_collection()
    if col is None:  
        return None
    return col.find_one({"hash": file_hash})
