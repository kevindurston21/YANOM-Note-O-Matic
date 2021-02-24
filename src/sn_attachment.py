from abc import ABC, abstractmethod
import sn_attachment_writer #import AttachmentWriter
from helper_functions import generate_clean_path
from sn_zipfile_reader import NSXZipFileReader


class Attachment(ABC):
    def __init__(self, json_data, attachment_id, notebook_folder_name, config_data, zipfile_reader: NSXZipFileReader):
        self.json = json_data
        self.attachment_id = attachment_id
        self.notebook_folder_name = notebook_folder_name
        self.config_data = config_data
        self.zipfile_reader = zipfile_reader
        self.name = self.json['name']
        self.file_name = ''
        self.path_relative_to_notebook = ''
        self.full_path = ''
        self.nsx_filename = f"file_{self.json['md5']}"
        self.html_link = ''
        super(Attachment, self).__init__()

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
        writer = sn_attachment_writer.AttachmentWriter(self.config_data, self.zipfile_reader)
        writer.store_attachment(self)

    def get_notebook_folder_name(self):
        return self.notebook_folder_name

    def get_file_name(self):
        return self.file_name

    def get_nsx_filename(self):
        return self.nsx_filename

    def set_relative_path(self, path):
        self.path_relative_to_notebook = path

    def get_relative_path(self):
        return self.path_relative_to_notebook

    def get_full_path(self):
        return self.full_path

    def set_file_name(self, file_name):
        self.file_name = file_name

    def set_full_path(self, path):
        self.full_path = path


class ImageAttachment(Attachment):

    def __init__(self, json_data, attachment_id, notebook_folder_name, config_data, zipfile_reader: NSXZipFileReader):
        super().__init__(json_data, attachment_id, notebook_folder_name, config_data, zipfile_reader)
        self.html_image_ref = self.json['ref']
        self.clean_name()

    def create_html_link(self):
        self.html_link = f"<img src={self.file_name} "

    def clean_name(self):
        self.name = self.name.replace('ns_attach_image_', '')
        self.file_name = generate_clean_path(self.name)


class FileAttachment(Attachment):

    def create_html_link(self):
        pass

    def clean_name(self):
        self.file_name = generate_clean_path(self.name)
