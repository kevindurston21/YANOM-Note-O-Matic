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
    def __init__(self, nsx_file):
        # self.zipfile_reader = zipfile_reader
        self.nsx_file = nsx_file
        self.current_directory_path = Path(__file__).parent.absolute()
        self.output_folder = nsx_file.get_config_data().get_output_folder()
        self.attachment_folder = nsx_file.get_config_data().get_attachment_folder()
        self.notebook_folder = None
        self.output_file_name = None
        self.input_file_name = None
        self.path_relative_to_notebook = None
        self.output_file_path = None
        self.relative_path = None

    def store_attachment(self, attachment):
        self.generate_relative_path(attachment)
        self.generate_output_path(attachment)
        Path(self.output_file_path).write_bytes(self.nsx_file.fetch_attachment_file(attachment.get_nsx_filename()))

    def generate_relative_path(self, attachment):
        self.path_relative_to_notebook = Path(self.attachment_folder, attachment.get_file_name())

    def generate_output_path(self, attachment):
        path = Path(self.current_directory_path, self.output_folder,
                    attachment.get_notebook_folder_name(),
                    self.path_relative_to_notebook)

        while path.is_file():
            path = generate_new_filename(path)

        self.output_file_name = path.stem
        self.output_file_path = path
        self.relative_path = (Path(self.attachment_folder, self.output_file_name))

    # def set_notebook_folder(self, notebook_folder):
    #     self.notebook_folder = notebook_folder

    def get_output_file_name(self):
        return self.output_file_name

    def get_output_file_path(self):
        return self.output_file_path

    def get_relative_path(self):
        return self.relative_path

