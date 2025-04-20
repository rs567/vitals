from pathlib import Path
from logger import logger, setup_logging
import logging 

setup_logging()
logger = logging.getLogger(__name__)

def get_unique_filename(file_path: Path) -> Path:
    '''
    add an incrementing number if a file already exists
    '''
    # Check if the file exists
    if not file_path.exists():
        return file_path  # If it doesn't exist, return the original path
    
    # If the file exists, start adding a counter to the filename
    base_filename = file_path.stem  # Get the base filename without extension
    extension = file_path.suffix  # Get the file extension
    counter = 1

    # Loop until a unique file name is found
    while file_path.exists():
        # Create a new filename with the counter appended
        new_filename = file_path.parent / f"{base_filename}_{counter}{extension}"
        file_path = new_filename
        counter += 1

    return file_path

class FileHandler:
    '''
    Handles file operations in for the app, the data folder, however can be 
    specified to write else where

    [not implemented yet]
    - index, manage files locally here without putting files into mongoDB
    '''
    DATA_FOLDER_PATH = Path('.') / 'Data'
    IMPORT_FOLDER_PATH = DATA_FOLDER_PATH / "import"
    OUTBOX_FOLDER_PATH = DATA_FOLDER_PATH / "outbox"
    BILLING_FOLDER_PATH = DATA_FOLDER_PATH / "billing"
    MEDICAL_RECORDS_FOLDER_PATH = DATA_FOLDER_PATH / "medical_records"

    def __init__(self):
        '''
        Initialize the FileHandler with a folder path.
        '''
        self.initalize_folders()

    def initalize_folders(self):
        '''
        make the folders locally in the repo if they aren't there already
        '''
        if not FileHandler.IMPORT_FOLDER_PATH.exists():
            FileHandler.IMPORT_FOLDER_PATH.mkdir(exist_ok=True)
        if not FileHandler.OUTBOX_FOLDER_PATH.exists():
            FileHandler.OUTBOX_FOLDER_PATH.mkdir(exist_ok=True)
        if not FileHandler.BILLING_FOLDER_PATH.exists():
            FileHandler.BILLING_FOLDER_PATH.mkdir(exist_ok=True)
        if not FileHandler.MEDICAL_RECORDS_FOLDER_PATH.exists():
            FileHandler.MEDICAL_RECORDS_FOLDER_PATH.mkdir(exist_ok=True)

    def list_files(self, cur_dir):
        '''
        list all files in the folder.
        cur_dir
            use the paths created as the instance attribute
        '''
        return [f.name for f in cur_dir.iterdir() if f.is_file()]

    def retrieve_file(self, file_name):
        '''
        Retrieve the full path of a file in the folder.
        '''
        file_path = self.folder_path / file_name
        if file_path.exists():
            return str(file_path)  # convert to string if needed
        else:
            raise FileNotFoundError(f"File '{file_name}' not found in the folder.")

    def delete_file(self, file_name):
        '''
        Delete a file from the folder.
        '''
        file_path = self.folder_path / file_name
        if file_path.exists():
            file_path.unlink()
            return f"File '{file_name}' has been deleted."
        else:
            raise FileNotFoundError(f"File '{file_name}' not found in the folder.")

    def update_file(self, file_name, new_content):
        '''
        Update the content of a file in the folder.
        If the file does not exist, it will be created.
        '''
        file_path = self.folder_path / file_name
        file_path.write_text(new_content)
        return f"File '{file_name}' has been updated."

    def watch_folder(self):
        '''
        Watch the folder for changes (basic implementation).
        '''
        logging.info(f"Watching folder: {self.folder_path}")
        initial_files = set(self.list_files())
        try:
            while True:
                current_files = set(self.list_files())
                added_files = current_files - initial_files
                removed_files = initial_files - current_files

                if added_files:
                    logging.info(f"New files added: {', '.join(added_files)}")
                if removed_files:
                    logging.info(f"Files removed: {', '.join(removed_files)}")

                initial_files = current_files
        except KeyboardInterrupt:
            logging.info("Stopped watching the folder.")
