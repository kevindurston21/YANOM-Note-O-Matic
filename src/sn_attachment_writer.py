from pathlib import Path
import sn_attachment  # import Attachment, ImageAttachment, FileAttachment
from config_data import ConfigData
from helper_functions import generate_clean_path
import random
import string


def get_random_string(length):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))


def generate_new_filename(path):
    stem = Path(path).stem
    stem = f"{stem}-{get_random_string(4)}"
    new_filename = f"{stem}{Path(path).suffix}"
    path = Path(Path(path).parent, new_filename)
    return path


class AttachmentWriter:
    def __init__(self, config_data: ConfigData, zipfile_reader):
        self.zipfile_reader = zipfile_reader
        self.current_directory_path = Path(__file__).parent.absolute()
        self.output_folder = config_data.get_output_folder()
        self.attachment_folder = config_data.get_attachment_folder()
        self.notebook_folder = ''
        self.output_file_name = ''
        self.input_file_name = ''
        self.path_relative_to_notebook = ''
        self.output_file_path = ''

    def store_attachment(self, attachment):
        self.generate_relative_path(attachment)
        self.generate_output_path(attachment)

        Path(attachment.get_full_path()).write_bytes(self.zipfile_reader.read_attachment_file(attachment.get_nsx_filename()))

    def generate_relative_path(self, attachment):
        # self.output_file_name = attachment.get_file_name()
        # self.input_file_name = attachment.get_nsx_filename()
        # self.notebook_folder = attachment.get_notebook_folder_name()
        # attachment.path_relative_to_notebook = self.generate_relative_path(attachment)
        attachment.set_relative_path(Path(self.attachment_folder, attachment.file_name))

        # attachment.set_relative_path(self.path_relative_to_notebook)

    # def generate_relative_path(self, attachment):
    #     # path = Path(attachment.attachment_folder, attachment.output_file_name)
    #     attachment.path_relative_to_notebook = Path(attachment.attachment_folder, attachment.output_file_name)

    def generate_output_path(self, attachment):
        path = Path(self.current_directory_path, self.output_folder,
                    attachment.get_notebook_folder_name(),
                    attachment.get_relative_path())

        while path.is_file():
            path = generate_new_filename(path)

        attachment.set_file_name(path.stem)
        attachment.set_full_path(path)
        # self.path_relative_to_notebook = self.generate_relative_path()
        attachment.set_relative_path(Path(self.attachment_folder, attachment.file_name))

    def set_notebook_folder(self, notebook_folder):
        self.notebook_folder = notebook_folder
