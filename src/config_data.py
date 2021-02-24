from helper_functions import generate_clean_path


class ConfigData:
    def __init__(self):
        self.config_from_file = {'attachment_folder': 'media'}
        self.attachment_folder = generate_clean_path(self.config_from_file['attachment_folder'])
        self.output_folder = 'notes'


    def get_attachment_folder(self):
        return self.attachment_folder


    def get_output_folder(self):
        return self.output_folder

