# database/db_handler.py
from pymongo import MongoClient
from config import MONGO_URI, DATABASE_NAME, CONNECTION_TIMEOUT
from datetime import datetime
from bson import ObjectId


class DatabaseHandler:
    def __init__(self):
        try:
            self.client = MongoClient(
                MONGO_URI, 
                serverSelectionTimeoutMS=CONNECTION_TIMEOUT,
                connectTimeoutMS=CONNECTION_TIMEOUT
            )
            self.client.server_info()
            
            self.db = self.client[DATABASE_NAME]
            self.passwords = self.db.passwords
            
            self._create_indexes()
            print("✅ Connected to MongoDB Atlas successfully!")
            
        except Exception as e:
            print("❌ MongoDB Connection Failed:", e)
            raise

    def _create_indexes(self):
        """Safely create indexes without conflicts"""
        try:
            # Drop old conflicting text index if it exists
            existing_indexes = self.passwords.index_information()
            for name, info in existing_indexes.items():
                if info.get('key') and '_fts' in str(info.get('key')):  # It's a text index
                    if name != "text_index":  # Different name
                        try:
                            self.passwords.drop_index(name)
                            print(f"🗑️ Dropped old index: {name}")
                        except:
                            pass

            # Create new consistent text index
            self.passwords.create_index(
                [("site", "text"), ("username", "text"), ("url", "text"), ("category", "text")],
                name="text_index",
                default_language="english"
            )
            
        except Exception as e:
            print("Warning: Could not update indexes:", e)

    def insert_password(self, data: dict):
        data["date_added"] = datetime.now()
        data["last_modified"] = datetime.now()
        return self.passwords.insert_one(data)

    def get_all_passwords(self):
        return list(self.passwords.find({}).sort("date_added", -1))

    def update_password(self, entry_id, new_data: dict):
        if isinstance(entry_id, str):
            entry_id = ObjectId(entry_id)
        
        new_data["last_modified"] = datetime.now()
        return self.passwords.update_one({"_id": entry_id}, {"$set": new_data})

    def delete_password(self, entry_id):
        if isinstance(entry_id, str):
            entry_id = ObjectId(entry_id)
        return self.passwords.delete_one({"_id": entry_id})

    def close(self):
        self.client.close()