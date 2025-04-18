from pathlib import Path


class FileHandler:
    def __init__(self):
        '''
        Initialize the FileHandler with a folder path.
        '''
        self.data_folder_path = Path('.') / 'Data'
        self.import_folder_path = self.data_folder_path / "import"
        self.outbox_folder_path = self.data_folder_path / "outbox"
        self.billing_folder_path = self.data_folder_path / "billing"
        self.medical_records_folder_path = self.data_folder_path / "medical_records"

        self.initalize_folders()

    def initalize_folders(self):
        '''
        make the folders locally in the repo if they aren't there already
        '''
        if not self.import_folder_path.exists():
            self.import_folder_path.mkdir(exist_ok=True)
        if not self.outbox_folder_path.exists():
            self.outbox_folder_path.mkdir(exist_ok=True)
        if not self.billing_folder_path.exists():
            self.billing_folder_path.mkdir(exist_ok=True)
        if not self.medical_records_folder_path.exists():
            self.medical_records_folder_path.mkdir(exist_ok=True)

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
        print(f"Watching folder: {self.folder_path}")
        initial_files = set(self.list_files())
        try:
            while True:
                current_files = set(self.list_files())
                added_files = current_files - initial_files
                removed_files = initial_files - current_files

                if added_files:
                    print(f"New files added: {', '.join(added_files)}")
                if removed_files:
                    print(f"Files removed: {', '.join(removed_files)}")

                initial_files = current_files
        except KeyboardInterrupt:
            print("Stopped watching the folder.")


test = FileHandler()
...