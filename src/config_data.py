from helper_functions import generate_clean_path
from configparser import ConfigParser
from pathlib import Path
import quick_settings
import logging


module_logger = logging.getLogger('yanom-application.config_data')


class ConfigException(Exception):
    pass


class ConfigData(ConfigParser):
    def __init__(self, config_file, default_quick_setting, **kwargs):
        super(ConfigData, self).__init__(**kwargs)
        self.logger = logging.getLogger('yanom-application.config_data.ConfigData')
        self.logger.debug('creating an instance of ConfigData')
        # Note: allow_no_value=True  allows for #comments in the ini file #comments are
        # treated as 'values' with no value.  To get the comment into the ini use a dictionary entry
        # where the key value pair are like this '#your comment': None
        # self.default_config = self.DefaultConfig()
        self.config_file = config_file
        self.default_quick_setting = default_quick_setting
        self.current_quick_setting = None
        self.load_quick_setting(default_quick_setting)

        self.read_config_file()
        self.validate_config_file()

    def validate_config_file(self):
        self.logger.debug("attempting to validate config file")
        try:
            self.validate_config()
            self.logger.info("config file validated")
        except ConfigException as e:
            logging.exception("Exception occurred validating config.ini")
            self.logger.warning("config file invalid")
            print("[d] Enter d to create a default configuration")
            print("[x] Enter x to exit and edit config.ini")
            while True:
                what_to_do = input('Choose default or to exit? : ')
                if what_to_do.lower() == 'x':
                    self.logger.info("user exiting")
                    exit(0)
                elif what_to_do.lower() == 'd':
                    self.logger.info("user chose to create default file")
                    self.load_quick_setting(self.default_quick_setting)
                    self.write_config_file()
                    break
                else:
                    print(f"{what_to_do} was not an option")


    def validate_config(self):
        required_values = {
            'quick_settings': {
                'quick_setting': ('manual', 'q_own_notes', 'obsidian', 'gfm', 'pdf')
            },
            'export_formats': {
                'export_format': ('q_own_notes', 'obsidian', 'gfm', 'pdf')
            },
            'meta_data_options': {
                'include_meta_data': ('yes', 'no'),
                'yaml_meta_header_format': ('yes', 'no'),
                'insert_title': ('yes', 'no'),
                'insert_creation_time': ('yes', 'no'),
                'insert_modified_time': ('yes', 'no'),
                'include_tags': ('yes', 'no'),
                'tag_prefix': '#',
                'no_spaces_in_tags': ('yes', 'no'),
                'split_tags': ('yes', 'no')
            },
            'file_options': {
                'export_folder_name': 'notes',
                'attachment_folder_name': 'attachments',
                'creation_time_in_exported_file_name': ('yes', 'no')
            },
            'image_link_formats': {'image_link_format': ('strict_md', 'obsidian', 'gfm-html')}
        }

        for section, keys in required_values.items():
            if section not in self:
                raise ConfigException(f'Missing section {section} in the config ini file')

            for key, values in keys.items():
                if key not in self[section] or self[section][key] == '':
                    raise ConfigException(f'Missing value for {key} under section {section} in the config ini file')

                if values:
                    if self[section][key] not in values:
                        raise ConfigException(f'Invalid value for {key} under section {section} in the config file')

    def write_config_file(self):
        with open(self.config_file, 'w') as config_file:
            self.write(config_file)

    def read_config_file(self):
        self.logger.debug('reading config file')
        path = Path(self.config_file)
        if path.is_file():
            self.read(self.config_file)
        else:
            self.logger.info('config.ini missing, generating new file and settings set to default.')
            print("config.ini missing, generating new file.")
            self.set_and_write_quick_settings(self.default_quick_set)

    def load_quick_setting(self, setting):
        self.current_quick_setting = quick_settings.please.provide(setting)
        self.read_dict(self.current_quick_setting.provide_quick_settings())
        pass


if __name__ == '__main__':
    # for testing
    my_config = ConfigData('config.ini', allow_no_value=True)
    # my_config.write_config_file()
    # my_config.default_config.set_quick_set_settings("gfm")
    # my_config.write_config_file()
    # my_config.read_config_file()
    print("Done")
