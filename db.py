import logging
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

class MongoDBConnection:
    def __init__(self, uri="mongodb://localhost:27017/", db_name=None):
        self.uri = uri
        self.db_name = db_name
        self.client = None
        self.db = None

        if not self.db_name:
            raise ValueError("Database name was not given at startup")
    
    def connect(self):
        try:
            self.client = MongoClient(self.uri)
            self.db = self.client[self.db_name]
            self.client.admin.command("ping")
            logging.info(f"Connected to MongoDB: {self.db_name}")
        except ConnectionFailure as e:
            logging.error(f"Connection failed: {e}")
            raise

    def get_collection(self, collection_name):
        if self.db is None:
            raise Exception("Not connected to MongoDB. Call connect() first.")
        return self.db[collection_name]
    
    def close(self):
        if self.client:
            self.client.close()
            logging.info("MongoDB connection closed.")

    def create_upload(self):
        ...


if __name__ == "__main__":
    mongo = MongoDBConnection(db_name="testdb")
    mongo.connect()
    users = mongo.get_collection("users")
    users.insert_one({
        "name": "Charlie",
        "age":  "30"
    })

    print(users.find_one({"name": "Charlie"}))

    ...

    mongo.close()