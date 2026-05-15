# database/db_handler.py
from pymongo import MongoClient
from config import MONGO_URI, DATABASE_NAME, CONNECTION_TIMEOUT
from datetime import datetime

class DatabaseHandler:
    def __init__(self):
        try:
            self.client = MongoClient(
                MONGO_URI, 
                serverSelectionTimeoutMS=CONNECTION_TIMEOUT,
                connectTimeoutMS=CONNECTION_TIMEOUT
            )
            # Test the connection
            self.client.server_info()
            
            self.db = self.client[DATABASE_NAME]
            self.passwords = self.db.passwords
            
            # Create text index for search
            self.passwords.create_index([("site", "text"), ("username", "text"), ("category", "text")])
            
            print("Successfully connected to MongoDB Atlas!")
            
        except Exception as e:
            print(" MongoDB Atlas Connection Failed!")
            print("Error:", e)
            raise
    
    def insert_password(self, data: dict):
        data["date_added"] = datetime.now()
        data["last_modified"] = datetime.now()
        return self.passwords.insert_one(data)
    
    def get_all_passwords(self):
        return list(self.passwords.find({}, {
            "_id": 1, 
            "site": 1, 
            "username": 1, 
            "category": 1, 
            "date_added": 1
        }).sort("date_added", -1))
    
    def delete_password(self, entry_id):
        return self.passwords.delete_one({"_id": entry_id})
    
    def close(self):
        self.client.close()