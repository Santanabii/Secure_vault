# test_connection.py
from pymongo import MongoClient
from config import MONGO_URI, DATABASE_NAME

print("🔄 Testing MongoDB Atlas Connection...\n")

try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=10000)
    client.server_info()
    print(" SUCCESS! Connected to MongoDB Atlas")
    print(f"Database: {DATABASE_NAME}")
    
    db = client[DATABASE_NAME]
    print("Collections:", db.list_collection_names())
    
except Exception as e:
    print("Connection Failed")
    print("Error:", e)