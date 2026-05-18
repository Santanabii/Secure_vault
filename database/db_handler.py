# database/db_handler.py
from pymongo import MongoClient
from config import MONGO_URI, DATABASE_NAME, CONNECTION_TIMEOUT
from datetime import datetime
from bson import ObjectId

class DatabaseHandler:
    def __init__(self):
        self.client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=CONNECTION_TIMEOUT)
        self.db = self.client[DATABASE_NAME]
        self.passwords = self.db.passwords
        print("✅ Connected to MongoDB Atlas!")

    def insert_password(self, data: dict, username: str):
        data["date_added"] = datetime.now()
        data["last_modified"] = datetime.now()
        data["owner"] = username.lower()
        return self.passwords.insert_one(data)

    def get_all_passwords(self, username: str):
        return list(self.passwords.find({"owner": username.lower()}).sort("date_added", -1))

    def update_password(self, entry_id, new_data: dict, username: str):
        if isinstance(entry_id, str):
            entry_id = ObjectId(entry_id)
        new_data["last_modified"] = datetime.now()
        new_data["owner"] = username.lower()
        return self.passwords.update_one(
            {"_id": entry_id, "owner": username.lower()}, 
            {"$set": new_data}
        )

    def delete_password(self, entry_id, username: str):
        if isinstance(entry_id, str):
            entry_id = ObjectId(entry_id)
        return self.passwords.delete_one({"_id": entry_id, "owner": username.lower()})