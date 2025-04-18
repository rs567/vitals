from pathlib import Path
import logging
from typing import List, Dict, Optional
from datetime import datetime, timezone
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import gridfs
from data.file_io import FileHandler

from bson import ObjectId

logging.basicConfig(
    level=logging.ERROR,
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
            self.fs = gridfs.GridFS(self.db)
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

    def create_document(self, path: Path, metadata: Optional[Dict] = None) -> Optional[str]:
        '''
        upload a file to db, move the folder 
        '''
        if not path.exists() or not path.is_file():
            logging.error(f"Error: The file {path} does not exist or is not a valid file.")
            return None
        if metadata is None:
            metadata = self.create_metadata()

        with path.open("rb") as file:
            file_id = self.fs.put(file, filename=path.name, metadata=metadata)

        logging.info(f"File uploaded with ID: {file_id}")
        return str(file_id)
    
    def create_metadata(self, tags: Optional[List[str]] = ["unsorted"], 
        date_of_service: Optional[str] = None, doctor: Optional[str] = "") -> Dict:
        
        '''
        fname:
            string, file name from path
        date_of_service: 
            defaults to current time 
            optional, user input date, datetime will parse
        tag options:
            bill, reciept, payment, lab_results, avs (after visit summary)
            rx, email
        doctor: 
            optional, name of the doctor
        '''
        if date_of_service:
            datetime.strptime(date_of_service, "%Y-%m-%d")
        else:
            date_of_service = datetime.now().date()

        metadata = {
            "date_of_service": "222",
            "upload_time": datetime.now(timezone.utc),
            "tags": tags,
            "doctor": doctor,
        }
        return metadata

    def update_metadata(self):
        ...

    def delete_document(self):
        ...
    
    def get_document(self, file_id: Optional[str] = None, filename: Optional[str] = None, 
        save_to: Optional[Path] = None) -> Optional[bytes]:
        """
        Retrieve a file from GridFS by ID or filename.
        If save_to is provided, saves the file to disk.
        Otherwise, returns the file's bytes.
        """
        if not file_id and not filename:
            logging.error("You must provide either file_id or filename.")
            return None

        try:
            if file_id:
                grid_out = self.fs.get(ObjectId(file_id))
            elif filename:
                grid_out = self.fs.find_one({"filename": filename})
                if grid_out is None:
                    logging.warning(f"No file found with filename '{filename}'.")
                    return None

            file_data = grid_out.read()

            if save_to:
                save_to.parent.mkdir(parents=True, exist_ok=True)
                with save_to.open("wb") as f:
                    f.write(file_data)
                logging.info(f"File saved to {save_to}")
                return None
            else:
                logging.info(f"File '{grid_out.filename}' retrieved from GridFS.")
                return file_data

        except Exception as e:
            logging.error(f"Error retrieving file: {e}")
            return None

    def list_file_ids(self) -> List[str]:
        """
        List all file IDs currently stored in GridFS.
        Returns a list of file IDs as strings.
        """
        if self.db is None:
            raise Exception("Not connected to MongoDB. Call connect() first.")

        file_ids = []
        for file_doc in self.db.fs.files.find():
            file_ids.append(str(file_doc["_id"]))

        return file_ids


if __name__ == "__main__":
    mongo = MongoDBConnection(db_name="testdb")
    mongo.connect()
    users = mongo.get_collection("users")
    test_path = Path(r"D:\repos\vitals\data\import\n_pain.md")
    file_id = mongo.create_document(test_path)
    print(file_id)

    mongo.get_document(
        file_id,
        save_to=Path(r"D:\repos\vitals\data\outbox\pain.md")
    )

    file_ids = mongo.list_file_ids()
    for file_id in file_ids:
        print(f"File ID: {file_id}")

    ...

    mongo.close()