from sn_config_data import ConfigData
from pathlib import Path
from helper_functions import generate_clean_path


#  when add pdf and html etc this is likely to be inherited from an abstract note writer.

class MDNoteWriter:
    def __init__(self, config_data: ConfigData):
        self.config_data = config_data
        self.current_directory_path = Path(__file__).parent.absolute()
        self.output_folder = config_data.get('file_options', 'export_folder_name')
        self.output_full_path = None
        self.output_file_name = None

    def store_file(self, note):
        Path(note.get_full_path()).write_text(note.get_converted_content(), 'utf-8')

    def generate_output_path_and_set_note_file_name(self, note):
        dirty_filename = note.get_title() + '.md'
        self.output_file_name = (generate_clean_path(dirty_filename))
        n = 0
        target_path = Path(self.current_directory_path, self.output_folder, note.get_notebook_folder_name(), self.output_file_name)
        while target_path.exists():
            n += 1
            target_path = Path(self.current_directory_path, self.output_folder, note.get_notebook_folder_name(), f"{Path(self.output_file_name).stem}-{n}{Path(self.output_file_name).suffix}")

        self.output_file_name = target_path.name
        self.output_full_path = target_path

    def get_output_full_path(self):
        return self.output_full_path

    def get_output_file_name(self):
        return self.output_file_name