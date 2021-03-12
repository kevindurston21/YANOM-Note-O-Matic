import sn_attachment
from helper_functions import generate_clean_path
from sn_note_writer import MDNoteWriter
import logging
from globals import APP_NAME
import inspect
from pre_processing import NoteStationPreProcessing


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
        self._nsx_file = nsx_file
        self._zipfile_reader = nsx_file.zipfile_reader
        self._note_writer = nsx_file.note_writer
        self._pandoc_converter = nsx_file.pandoc_converter
        self._conversion_settings = nsx_file.conversion_settings
        self._note_writer = nsx_file.note_writer
        self._note_id = note_id
        self._note_json = nsx_file.fetch_json_data(note_id)
        self._title = self._note_json['title']
        self._creation_time = self._note_json['ctime']
        self._modified_time = self._note_json['mtime']
        self._raw_content = self._note_json['content']
        self._parent_notebook = self._note_json['parent_id']
        self._attachments_json = self._note_json['attachment']
        self._attachments = {}
        self._pre_processed_content = ''
        self._converted_content = ''
        self._notebook_folder_name = ''
        self._file_name = ''
        self._full_path = ''
        self._image_count = 0
        self._attachment_count = 0

    def process_note(self):
        self.logger.info(f"Processing note page '{self._title}' - {self._note_id}")
        self.create_attachments()
        self.process_attachments()
        self.pre_process_content()
        self.convert_data()
        self._note_writer.generate_output_path_and_set_note_file_name(self)
        self.update_paths_and_filenames()
        self._note_writer.store_file(self)
        self.logger.info(f"Processing of note page '{self._title}' - {self._note_id}  completed.")

    def get_parent_notebook_id(self):
        return self._parent_notebook

    def create_attachments(self):
        for attachment_id in self._attachments_json:
            if self._attachments_json[attachment_id]['type'].startswith('image'):
                self._attachments[attachment_id] = sn_attachment.ImageNSAttachment(self, attachment_id)
                self._image_count += 1
            else:
                self._attachments[attachment_id] = sn_attachment.FileNSAttachment(self, attachment_id)
                self._attachment_count += 1
        return self._image_count, self._attachment_count

    def process_attachments(self):
        for attachment_id in self._attachments:
            self._attachments[attachment_id].process_attachment()

    def pre_process_content(self):
        pre_processor = NoteStationPreProcessing(self)
        self._pre_processed_content = pre_processor.pre_processed_content

    def convert_data(self):
        self.logger.info(f"Converting content of '{self._title}' - {self._note_id}")
        self._converted_content = self._pandoc_converter.convert_using_strings(self._pre_processed_content, self._title)

    def create_file_writer(self):
        self._note_writer = MDNoteWriter(self._conversion_settings)

    def update_paths_and_filenames(self):
        self._file_name = self._note_writer.get_output_file_name()
        self._full_path = self._note_writer.get_output_full_path()

    @property
    def title(self):
        return self._title

    @property
    def note_id(self):
        return self._note_id

    @property
    def notebook_folder_name(self):
        return self._notebook_folder_name

    @notebook_folder_name.setter
    def notebook_folder_name(self, title):
        self._notebook_folder_name = generate_clean_path(title)

    @property
    def file_name(self):
        return self._file_name

    @property
    def full_path(self):
        return self._full_path

    @property
    def converted_content(self):
        return self._converted_content

    @property
    def json_data(self):
        return self._note_json

    @property
    def pre_processed_content(self):
        return self._pre_processed_content

    @property
    def nsx_file(self):
        return self._nsx_file

    @property
    def raw_content(self):
        return self._raw_content

    @property
    def attachments(self):
        return self._attachments

    @property
    def image_count(self):
        return self._image_count

    @image_count.setter
    def image_count(self, value):
        self._image_count = value

    @property
    def attachment_count(self):
        return self._attachment_count

    @attachment_count.setter
    def attachment_count(self, value):
        self._attachment_count = value
