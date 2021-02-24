#  at some point need to add recycle bin  should be create new note book
from helper_functions import generate_clean_path
import zipfile
import json
from sn_note_page import NotePage
from sn_zipfile_reader import NSXZipFileReader
from helper_functions import generate_clean_path
from pathlib import Path


class Notebook:
    def __init__(self, nsx_file, notebook_id):
        self.nsx_file = nsx_file
        self.notebook_id = notebook_id
        # self.zipfile_reader = self.nsx_file.zipfile_reader
        self.config_data = self.nsx_file.get_config_data()
        self.notebook_json = ''
        if self.notebook_id == 'recycle_bin':
            self.title = 'recycle_bin'
        if self.notebook_id != 'recycle_bin':
            self.fetch_notebook_data()
            self.title = self.notebook_json['title']
        self.folder_name = ''
        self.create_folder_name()
        self.full_path_to_notebook = ''
        self.note_pages = []

    def fetch_notebook_data(self):
        self.notebook_json = self.nsx_file.get_zipfile_reader().read_json_data(self.notebook_id)

    def process_notebook_pages(self):
        for note_page in self.note_pages:
            note_page.process_note()

    def add_note_page_and_set_parent_notebook(self, note_page: NotePage):
        note_page.set_notebook_folder_name(self.folder_name)
        self.note_pages.append(note_page)

    def create_folder_name(self):
        self.folder_name = generate_clean_path(self.title)

    def create_folders(self):
        self.create_notebook_folder()
        self.create_attachment_folder()

    def create_notebook_folder(self):
        n = 0
        target_path = Path(Path(__file__).parent.absolute(), self.nsx_file.config_data.output_folder, self.folder_name)
        while target_path.exists():
            n += 1
            target_path = Path(Path(__file__).parent.absolute(), self.nsx_file.config_data.output_folder, f"{self.folder_name}-{n}")

        target_path.mkdir()
        self.folder_name = target_path.stem
        self.full_path_to_notebook = target_path

    def create_attachment_folder(self):
        Path(self.full_path_to_notebook, self.config_data.get_attachment_folder()).mkdir()

