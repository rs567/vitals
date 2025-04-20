import logging
from logger import logger, setup_logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Union

import gridfs
from bson import ObjectId
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

from data.file_io import FileHandler, get_unique_filename

setup_logging()
logger = logging.getLogger(__name__)

class MongoDBConnection:
    def __init__(self, uri="mongodb://localhost:27017/", db_name=None):
        self.uri = uri
        self.db_name = db_name
        self.client = None
        self.db = None
        self.fs = None

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

    def create_document(self, path: Path, metadata: Optional[Dict] = None) -> Optional[ObjectId]:
        '''
        upload a file to db, move the folder 
        '''
        # Checks
        if not path.exists() or not path.is_file():
            logging.error(f"Error: The file {path} does not exist or is not a valid file.")
            return None
        
        # Metedata Generation 
        if metadata is None:
            metadata = self.create_metadata()

        # Add File to DB
        with path.open("rb") as file:
            file_id = self.fs.put(file, filename=path.name, metadata=metadata)

        logging.info(f"File uploaded with ID: {file_id}")
        return ObjectId(file_id)
    
    def get_document(self, file_id: Optional[ObjectId] = None) -> Union[None, bytes]:
        '''
        get the binary of the file
        '''
        if not file_id:
            logging.error("You must provide either file_id")
            return None
        try:
            grid_out = self.fs.get(file_id)
            file_data = grid_out.read()
            logging.info(f"File '{grid_out.filename}' retrieved from GridFS.")
            return file_data
        except Exception as e:
            logging.error("Error retrieving file: {e}")
            return None

    def export_document(self, file_id: Optional[ObjectId] = None, 
            save_to: Optional[Path] = None) -> None:
        '''
        file_id
        save_to
            dir to save data to, filename will be what the original file was
        '''
        if not file_id:
            logging.error("You must provide either file_id")
            return None

        try:
            if save_to:
                if not save_to.exists() and not save_to.is_dir():
                    raise FileNotFoundError(f"Save path doesn't exist {save_to}")
            else: 
                current_date = datetime.today().strftime('%Y_%m_%d')
                save_to = FileHandler.OUTBOX_FOLDER_PATH / f"{current_date}_export"
                if not save_to.exists():
                    save_to.mkdir(exist_ok=True)
                    
            if file_id:
                grid_out = self.fs.get(file_id)
                save_to = get_unique_filename(save_to / grid_out.filename)

            file_data = grid_out.read()
            if save_to:
                save_to.parent.mkdir(parents=True, exist_ok=True)
                with save_to.open("wb") as f:
                    f.write(file_data)
                logging.info(f"File saved to {save_to}")

        except Exception as e:
            logging.error(f"Error retrieving file: {e}")
            return None
        
        except FileNotFoundError as e:
            logging.error(f"FileNotFoundError: {e}")
            return None
    
    def export_all_documents(self) -> None:
        file_ids = self.list_file_ids()
        current_date = datetime.today().strftime('%Y_%m_%d')
        save_to = FileHandler.OUTBOX_FOLDER_PATH / f"{current_date}_export_all"

        for id in file_ids:
            self.export_document(id, save_to)

    def delete_document(self, file_id: ObjectId):
        self.fs.delete(file_id=file_id)

    def create_metadata(self, path: Optional[Path], tags: Optional[List[str]] = ["unsorted"], 
        date_of_service: Optional[str] = None, doctor: Optional[str] = None) -> Dict:
        
        '''
        path:
            pathlib path, to get file creation date
        date_of_service: 
            defaults to current time 
            optional, user input date, datetime will parse
        tag options:
            bill, reciept, payment, lab_results, avs (after visit summary)
            rx, email
        doctor: 
            optional, name of the doctor
        '''
        try:
            created_time = datetime.datetime.fromtimestamp(path.stat().st_ctime)
        except:
            created_time = None

        if date_of_service:
            date_of_service = datetime.strptime(date_of_service, "%Y-%m-%d")
        else:
            date_of_service = None

        metadata = {
            "file_creation_time": created_time,
            "date_of_service": date_of_service,
            "upload_time": datetime.now(timezone.utc),
            "tags": tags,
            "doctor": doctor,
        }
        return metadata

    def update_metadata(self, file_id: Optional[ObjectId], date_of_service: Optional[str] = None, 
        doctor: Optional[str] = None, tags: Optional[List[str]] = None, **kwargs) -> None:
        '''
        update the exisiting metadata structure, can add/mod additional tags
        returns None when failed
        '''
        new_metadata = {}
        if date_of_service:
            new_metadata["metadata.date_of_service"] = date_of_service
        if doctor:
            new_metadata["metadata.doctor"] = doctor
        if tags:
            new_metadata["metadata.tags"] = tags

        for key, value in kwargs.items():
            new_metadata[f"metadata.{key}"] = value

        try:
            self.db.fs.files.update_one(
                filter={"_id": file_id},
                update={"$set": new_metadata}
            )
        
        except Exception as e:
            logging.error("Failed to update metadata")
            return None

    def get_metadata(self, file_id: Optional[ObjectId])-> Dict:
        '''
        returns dict, metadata tag of an object
        '''
        file_data = self.fs.get(file_id)
        return file_data.metadata

    def list_file_ids(self, print_ids: Optional[bool] = False) -> List[ObjectId]:
        '''
        retuns, list of ObjectIds, of all objs in the db
        '''
        if self.db is None:
            raise Exception("Not connected to MongoDB. Call connect() first.")

        file_ids = []
        for file_doc in self.db.fs.files.find():
            file_ids.append(file_doc["_id"])

        if print_ids:
            for id in file_id:
                print(str(id))
                logging.info(str(id))

        return file_ids


if __name__ == "__main__":
    mongo = MongoDBConnection(db_name="testdb")
    mongo.connect()
    users = mongo.get_collection("users")
    # test_path = Path(r"D:\repos\vitals\data\import\n_pain.md")
    # file_id = mongo.create_document(test_path)
    # print(file_id)

    # mongo.get_document(
    #     file_id,
    #     save_to=Path(r"D:\repos\vitals\data\outbox\pain.md")
    # )

    file_ids = mongo.list_file_ids()
    for file_id in file_ids:
        print(f"File ID: {file_id}")

    mongo.close()