from abc import ABC, abstractmethod
import sn_attachment_writer
from helper_functions import generate_clean_path


class Attachment(ABC):
    def __init__(self, note, attachment_id, nsx_file):
        self.nsx_file = nsx_file
        self.json = note.get_json_data()
        self.attachment_id = attachment_id
        self.notebook_folder_name = note.get_notebook_folder_name()
        self.conversion_settings = nsx_file.conversion_settings
        self.name = self.json['attachment'][attachment_id]['name']
        self.file_name = ''
        self.path_relative_to_notebook = ''
        self.full_path = ''
        self.filename_inside_nsx = f"file_{self.json['attachment'][attachment_id]['md5']}"
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
        attachment_writer = sn_attachment_writer.AttachmentWriter(self.nsx_file)
        attachment_writer.store_attachment(self)
        self.get_updated_files_and_folders_from(attachment_writer)

    def get_updated_files_and_folders_from(self, attachment_writer):
        self.file_name = attachment_writer.get_output_file_name()
        self.full_path = attachment_writer.get_output_file_path()
        self.path_relative_to_notebook = attachment_writer.get_relative_path()

    def get_notebook_folder_name(self):
        return self.notebook_folder_name

    def get_file_name(self):
        return self.file_name

    def get_nsx_filename(self):
        return self.filename_inside_nsx

    def get_relative_path(self):
        return self.path_relative_to_notebook

    def get_full_path(self):
        return self.full_path

    def get_filename_inside_nsx(self):
        return self.filename_inside_nsx


class ImageAttachment(Attachment):

    def __init__(self, note, attachment_id, nsx_file):
        super().__init__(note, attachment_id, nsx_file)
        self.html_image_ref = self.json['attachment'][attachment_id]['ref']

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
