import sn_attachment
from helper_functions import generate_clean_path
from sn_note_writer import MDNoteWriter
import logging
from globals import APP_NAME
import inspect


def what_module_is_this():
    return __name__


def what_method_is_this():
    return inspect.currentframe().f_back.f_code.co_name


def what_class_is_this(obj):
    return obj.__class__.__name__


class NotePage:
    def __init__(self, nsx_file, note_id, ):
        self.logger = logging.getLogger(f'{APP_NAME}.{what_module_is_this()}.{what_class_is_this(self)}')
        self.logger.setLevel(logging.DEBUG)
        self.nsx_file = nsx_file
        self.zipfile_reader = nsx_file.get_zipfile_reader()
        self.note_writer = nsx_file.get_note_writer()
        self.pandoc_converter = nsx_file.get_pandoc_converter()
        self.conversion_settings = nsx_file.get_conversion_settings()
        self.note_writer = nsx_file.get_note_writer()
        self.note_id = note_id
        self.note_json = nsx_file.fetch_json_data(note_id)
        self.title = self.note_json['title']
        self.creation_time = self.note_json['ctime']
        self.modified_time = self.note_json['mtime']
        self.raw_content = self.note_json['content']
        self.parent_notebook = self.note_json['parent_id']
        self.attachments_json = self.note_json['attachment']
        self.attachments = {}
        self.converted_content = ''
        self.notebook_folder_name = ''
        self.file_name = ''
        self.full_path = ''

    def process_note(self):
        self.logger.info(f"Processing note page '{self.title}' - {self.note_id}")
        self.create_attachments()
        self.process_attachments()
        self.convert_data()
        self.note_writer.generate_output_path_and_set_note_file_name(self)
        self.update_paths_and_filenames()
        self.note_writer.store_file(self)
        self.logger.info(f"Processing of note page '{self.title}' - {self.note_id}  completed.")

    def get_parent_notebook_id(self):
        return self.parent_notebook

    def create_attachments(self):
        for attachment_id in self.attachments_json:
            if self.attachments_json[attachment_id]['type'].startswith('image'):
                self.attachments[attachment_id] = sn_attachment.ImageAttachment(self, attachment_id, self.nsx_file)
            else:
                self.attachments[attachment_id] = sn_attachment.FileAttachment(self, attachment_id, self.nsx_file)

    def process_attachments(self):
        for attachment_id in self.attachments:
            self.attachments[attachment_id].process_attachment()

    def convert_data(self):
        self.logger.info(f"Converting content of '{self.title}' - {self.note_id}")
        self.converted_content = self.pandoc_converter.convert_using_strings(self.raw_content, self.title)

    def create_file_writer(self):
        self.note_writer = MDNoteWriter(self.conversion_settings)

    def update_paths_and_filenames(self):
        self.file_name = self.note_writer.get_output_file_name()
        self.full_path = self.note_writer.get_output_full_path()

    def set_notebook_folder_name(self, title):
        self.notebook_folder_name = generate_clean_path(title)

    def get_title(self):
        return self.title

    def get_note_id(self):
        return self.note_id

    def get_notebook_folder_name(self):
        return self.notebook_folder_name

    def get_file_name(self):
        return self.file_name

    def get_full_path(self):
        return self.full_path

    def get_converted_content(self):
        return self.converted_content

    def get_json_data(self):
        return self.note_json
