import logging
from globals import APP_NAME
from helper_functions import generate_new_filename
import inspect
from pathlib import Path


def what_module_is_this():
    return __name__


def what_method_is_this():
    return inspect.currentframe().f_back.f_code.co_name


def what_class_is_this(obj):
    return obj.__class__.__name__


class AttachmentWriter:
    def __init__(self, nsx_file):
        self.logger = logging.getLogger(f'{APP_NAME}.{what_module_is_this()}.{what_class_is_this(self)}')
        self.logger.setLevel(logging.DEBUG)
        self.logger.info(f'{__name__} - Creating an instance of {what_class_is_this(self)}')
        self.nsx_file = nsx_file
        self.current_directory_path = Path(__file__).parent.absolute()
        self.output_folder = nsx_file._conversion_settings.export_folder_name
        self.attachment_folder = nsx_file._conversion_settings.attachment_folder_name
        self.notebook_folder = None
        self.output_file_name = None
        self.input_file_name = None
        self.path_relative_to_notebook = None
        self.output_file_path = None
        self.relative_path = None

    def store_attachment(self, attachment):
        self.generate_relative_path(attachment)
        self.generate_output_path(attachment)
        self.logger.info(f"Storing attachment {attachment.get_file_name()} as {self.output_file_name}")
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

    def get_output_file_name(self):
        return self.output_file_name

    def get_output_file_path(self):
        return self.output_file_path

    def get_relative_path(self):
        return self.relative_path

