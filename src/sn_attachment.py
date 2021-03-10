from abc import ABC, abstractmethod
import sn_attachment_writer
from helper_functions import generate_clean_path


class Attachment(ABC):
    def __init__(self, note, attachment_id, nsx_file):
        super(Attachment, self).__init__()
        self._nsx_file = nsx_file
        self._json = note.json_data
        self._attachment_id = attachment_id
        self._notebook_folder_name = note._notebook_folder_name
        self._conversion_settings = nsx_file._conversion_settings
        self._name = self._json['attachment'][attachment_id]['name']
        self._file_name = ''
        self._path_relative_to_notebook = ''
        self._full_path = ''
        self._filename_inside_nsx = f"file_{self._json['attachment'][attachment_id]['md5']}"
        self._html_link = ''

    @abstractmethod
    def create_html_link(self):
        pass

    @abstractmethod
    def clean_name(self):
        pass

    def process_attachment(self):
        self.clean_name()
        self.store_attachment()
        self.create_html_link()

    def store_attachment(self):
        attachment_writer = sn_attachment_writer.AttachmentWriter(self._nsx_file)
        attachment_writer.store_attachment(self)
        self.get_updated_files_and_folders_from(attachment_writer)

    def get_updated_files_and_folders_from(self, attachment_writer):
        self._file_name = attachment_writer.get_output_file_name()
        self._full_path = attachment_writer.get_output_file_path()
        self._path_relative_to_notebook = attachment_writer.get_relative_path()

    @property
    def notebook_folder_name(self):
        return self._notebook_folder_name

    @property
    def file_name(self):
        return self._file_name

    @property
    def path_relative_to_notebook(self):
        return self._path_relative_to_notebook

    @property
    def full_path(self):
        return self._full_path

    @property
    def filename_inside_nsx(self):
        return self._filename_inside_nsx


class ImageAttachment(Attachment):

    def __init__(self, note, attachment_id, nsx_file):
        super().__init__(note, attachment_id, nsx_file)
        self._image_ref = self._json['attachment'][attachment_id]['ref']

    @property
    def image_ref(self):
        return self._image_ref

    def create_html_link(self):
        self._html_link = f"<img src={self._file_name} "

    def clean_name(self):
        self._name = self._name.replace('ns_attach_image_', '')
        self._file_name = generate_clean_path(self._name)


class FileAttachment(Attachment):

    def create_html_link(self):
        pass

    def clean_name(self):
        self._file_name = generate_clean_path(self._name)
