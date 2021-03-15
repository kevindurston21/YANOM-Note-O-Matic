import logging
from globals import APP_NAME
from helper_functions import generate_clean_path
import inspect
from pathlib import Path


def what_module_is_this():
    return __name__


def what_method_is_this():
    return inspect.currentframe().f_back.f_code.co_name


def what_class_is_this(obj):
    return obj.__class__.__name__

#  when add pdf and html etc this is likely to be inherited from an abstract note writer.


class MDNoteWriter:
    def __init__(self, conversion_settings):
        self.logger = logging.getLogger(f'{APP_NAME}.{what_module_is_this()}.{what_class_is_this(self)}')
        self.logger.setLevel(logging.DEBUG)
        self.conversion_settings = conversion_settings
        self.current_directory_path = Path(__file__).parent.absolute()
        self.output_folder = conversion_settings.export_folder_name
        self.output_full_path = None
        self.output_file_name = None

    def store_file(self, note):
        self.logger.info(f"Storing note '{note.get_title()}' as '{self.output_file_name}' "
                         f"in notebook folder '{note.get_notebook_folder_name()}'")
        Path(note.get_full_path()).write_text(note.get_converted_content(), 'utf-8')

    def generate_output_path_and_set_note_file_name(self, note):
        dirty_filename = note.get_title() + '.md'
        self.output_file_name = (generate_clean_path(dirty_filename))
        n = 0
        target_path = Path(self.current_directory_path, self.output_folder,
                           note.get_notebook_folder_name(), self.output_file_name)
        while target_path.exists():
            n += 1
            target_path = Path(self.current_directory_path, self.output_folder, note.get_notebook_folder_name(),
                               f"{Path(self.output_file_name).stem}-{n}{Path(self.output_file_name).suffix}")

        self.output_file_name = target_path.name
        self.output_full_path = target_path

    def get_output_full_path(self):
        return self.output_full_path

    def get_output_file_name(self):
        return self.output_file_name
