from sn_note_page import NotePage
from helper_functions import generate_clean_path
from pathlib import Path
import logging
from globals import APP_NAME
import inspect


def what_module_is_this():
    return __name__


def what_method_is_this():
    return inspect.currentframe().f_back.f_code.co_name


def what_class_is_this(obj):
    return obj.__class__.__name__


class Notebook:
    def __init__(self, nsx_file, notebook_id):
        self.logger = logging.getLogger(f'{APP_NAME}.{what_module_is_this()}.{what_class_is_this(self)}')
        self.logger.setLevel(logging.DEBUG)
        self.nsx_file = nsx_file
        self.notebook_id = notebook_id
        self.conversion_settings = self.nsx_file.get_conversion_settings()
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
        self.logger.info(f"Processing note book {self.title} - {self.notebook_id}")
        for note_page in self.note_pages:
            note_page.process_note()

    def add_note_page_and_set_parent_notebook(self, note_page: NotePage):
        self.logger.info(f"Adding note '{note_page.get_title()}' - {note_page.get_note_id()} "
                         f"to Notebook '{self.title}' - {self.notebook_id}")
        note_page.set_notebook_folder_name(self.folder_name)
        self.note_pages.append(note_page)

    def create_folder_name(self):
        self.folder_name = generate_clean_path(self.title)

    def create_folders(self):
        self.create_notebook_folder()
        self.create_attachment_folder()

    def create_notebook_folder(self):
        n = 0
        target_path = Path(Path(__file__).parent.absolute(),
                           self.nsx_file.conversion_settings.export_folder_name,
                           self.folder_name)
        while target_path.exists():
            n += 1
            target_path = Path(Path(__file__).parent.absolute(),
                               self.nsx_file.conversion_settings.export_folder_name,
                               f"{self.folder_name}-{n}")

        target_path.mkdir()
        self.folder_name = target_path.stem
        self.full_path_to_notebook = target_path

    def create_attachment_folder(self):
        Path(self.full_path_to_notebook, self.conversion_settings.attachment_folder_name).mkdir()

