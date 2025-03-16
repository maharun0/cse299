import pymongo
import gridfs

def connect_to_MongoDB(db_name, uri="mongodb://localhost:27017"):
    """
    Connects to MongoDB and returns the database and GridFS instance.
    """
    try:
        client = pymongo.MongoClient(
            uri, 
            serverSelectionTimeoutMS=5000
        )
        db = client[db_name]
        fs = gridfs.GridFS(db)
        client.server_info()
        print("✅ Connected to MongoDB")
        return db, fs
    except Exception as e:
        print(f"❌ MongoDB Connection Failed: {e}")
        return None, None

# Example usage
if __name__ == "__main__":
    db, fs = connect_to_MongoDB()
