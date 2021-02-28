from sn_notebook import Notebook
from sn_note_page import NotePage
from sn_zipfile_reader import NSXZipFileReader
from config_data import ConfigData
from sn_note_writer import MDNoteWriter
from sn_pandoc_converter import PandocConverter
import logging
from globals import APP_NAME
import inspect


def what_module_is_this():
    return __name__


def what_method_is_this():
    return inspect.currentframe().f_back.f_code.co_name


def what_class_is_this(obj):
    return obj.__class__.__name__


class NSXFile:

    def __init__(self, file, config_data: ConfigData):
        self.logger = logging.getLogger(f'{APP_NAME}.{what_module_is_this()}.{what_class_is_this(self)}')
        self.logger.setLevel(logging.DEBUG)
        self.logger.info(f'{__name__} - Creating an instance of {what_class_is_this(self)}')
        self.config_data = config_data
        self.nsx_file_name = file
        self.zipfile_reader = NSXZipFileReader(self.nsx_file_name)
        self.nsx_json_data = ''
        self.notebook_ids = None
        self.note_page_ids = None
        self.notebooks = {}
        self.note_pages = {}
        self.note_writer = None
        self.pandoc_converter = PandocConverter(config_data.get('export_formats', 'export_format'))

    def process_nsx_file(self):
        self.logger.info(f"Processing {self.nsx_file_name}")
        self.create_note_writer()
        self.nsx_json_data = self.fetch_json_data('config.json')
        self.notebook_ids = self.nsx_json_data['notebook']
        self.note_page_ids = self.nsx_json_data['note']
        self.add_notebooks()
        self.add_recycle_bin_notebook()
        self.create_folders()
        self.add_note_pages()
        self.add_note_pages_to_notebooks()
        self.process_notebooks()
        self.create_attachments()
        self.logger.info(f"Processing of {self.nsx_file_name} complete.")

    def do_something(self):
        print(self.nsx_file_name)

    def fetch_json_data(self, data_id):
        return self.zipfile_reader.read_json_data(data_id)

    def fetch_attachment_file(self, file_name):
        return self.zipfile_reader.read_attachment_file(file_name)

    def add_notebooks(self):
        self.notebooks = {
            notebook_id: Notebook(self, notebook_id)
            for notebook_id in self.notebook_ids
        }

    def add_recycle_bin_notebook(self):
        self.notebooks['recycle_bin'] = Notebook(self, 'recycle_bin')

    def create_folders(self):
        for notebooks_id in self.notebooks:
            self.notebooks[notebooks_id].create_folders()

    def add_note_pages(self):
        self.note_pages = {
            note_id: NotePage(self, note_id)
            for note_id in self.note_page_ids
        }

    def add_note_pages_to_notebooks(self):
        for note_page_id in self.note_pages:
            current_parent_id = self.note_pages[note_page_id].get_parent_notebook_id()
            if current_parent_id in self.notebooks:
                self.notebooks[current_parent_id].add_note_page_and_set_parent_notebook(self.note_pages[note_page_id])
            else:
                self.notebooks['recycle_bin'].add_note_page_and_set_parent_notebook(self.note_pages[note_page_id])

    def create_note_writer(self):
        self.note_writer = MDNoteWriter(self.config_data)

    def create_attachments(self):
        for note_page_id in self.note_pages:
            self.note_pages[note_page_id].create_attachments()

    def process_notebooks(self):
        for notebooks_id in self.notebooks:
            self.notebooks[notebooks_id].process_notebook_pages()

    def get_note_book_id(self):
        return self.notebooks

    def get_file_name(self):
        return self.nsx_file_name

    def get_config_data(self):
        return self.config_data

    def get_zipfile_reader(self):
        return self.zipfile_reader

    def get_note_writer(self):
        return self.note_writer

    def get_pandoc_converter(self):
        return self.pandoc_converter
