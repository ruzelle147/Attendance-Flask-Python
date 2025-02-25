from pymongo import MongoClient

# Connection URI
MONGO_URI = "mongodb+srv://ruzellegabriel:qwe123@cluster.42ut6.mongodb.net/attendance?retryWrites=true&w=majority"

try:
    client = MongoClient(MONGO_URI)
    db = client["attendance"]  # Replace with your actual database name
    collections = db.list_collection_names()  # Get list of collections
    print("Connected Successfully! Collections:", collections)
except Exception as e:
    print("MongoDB Connection Error:", e)
