from helper_functions import generate_clean_path
from configparser import ConfigParser
from pathlib import Path


class ConfigException(Exception):
    pass


class ConfigData(ConfigParser):
    def __init__(self, config_file, **kwargs):
        super(ConfigData, self).__init__(**kwargs)
        # Note: allow_no_value=True  allows for #comments in the ini file #comments are
        # treated as 'values' with no value.  To get the comment into the ini use a dictionary entry
        # where the key value pair are line this '#your comment': None
        self.default_config = self.DefaultConfig()
        self.default_quick_set = 'gfm'
        self.config_file = config_file
        self.read_config_file()
        self.try_to_validate_config_file()
        self.set_and_write_quick_settings(self.get('quick_settings', 'quick_setting'))

        # old stuff below
        self.config_from_file = {'attachment_folder': 'media'}
        self.attachment_folder = generate_clean_path(self.config_from_file['attachment_folder'])
        self.output_folder = 'notes'
        # old stuff above

    def try_to_validate_config_file(self):
        try:
            self.validate_config()
        except ConfigException as e:
            print(e)
            print("[d] Enter d to create a default configuration")
            print("[x] Enter x to exit and edit config.ini")
            while True:
                what_to_do = input('Choose default or to exit? : ')
                if what_to_do.lower() == 'x':
                    exit(0)
                elif what_to_do.lower() == 'd':
                    self.set_and_write_quick_settings(self.default_quick_set)
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
                'media_folder_name': 'attachments',
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

    def set_and_write_quick_settings(self, quick_set_setting):
        self.read_dict(self.default_config.set_quick_set_settings(quick_set_setting))
        self.write_config_file()

    def write_config_file(self):
        with open(self.config_file, 'w') as config_file:
            self.write(config_file)

    def read_config_file(self):
        path = Path(self.config_file)
        if path.is_file():
            self.read(self.config_file)
        else:
            print("config.ini missing, generating new file.")
            self.set_and_write_quick_settings(self.default_quick_set)

    def set_default_config(self):
        self.read_dict(self.default_config.set_quick_set_settings('q_own_notes'))

    class DefaultConfig:
        def __init__(self):
            self.output_file_types = ['md', 'pdf']
            self.valid_export_formats = ['manual', 'q_own_notes', 'obsidian', 'gfm', 'pdf']
            self.quick_settings = {}
            self.current_quick_set = ''   # this may not be needed currently set and never used.. probably a good idea at the time...
            self.export_formats = {}
            self.meta_data_options = {}
            self.file_options = {}
            self.image_link_formats = {}

        def default_quick_settings(self):
            self.quick_settings = {f'    # Valid entries are {", ".join(self.valid_export_formats)[:-2]}': None,
                                   '    # use manual to use manual settings below': None,
                                   '    # NOTE is an option other than - manual - is used the rest of the '
                                   '    # settings in this file will be set automatically'
                                   '    #': None,
                                   "quick_setting": 'gfm',
                                   '    # ': None,
                                   '    # The following sections only apply if all of the above are no': None,
                                   '    #': None}

        def default_export_formats(self):
            self.export_formats = {f'    # Valid entries are {", ".join(self.valid_export_formats)[:-2]}': None,
                                   "export_format": "gfm"}

        def default_meta_data_options(self):
            # if you change this changes are likely in all places that call this method
            self.meta_data_options = {'include_meta_data': 'yes',
                                      '    # Note if include_meta_data = no then the following values will': None,
                                      '    # not be included in the export file': None,
                                      'yaml_meta_header_format': 'no', 'insert_title': 'yes',
                                      'insert_creation_time': 'yes', 'insert_modified_time': 'yes',
                                      'include_tags': 'yes', 'tag_prefix': '#',
                                      'no_spaces_in_tags': 'yes', 'split_tags': 'no'}

        def default_file_options(self):
            # if you change this changes are likely in all places that call this method
            self.file_options = {'export_folder_name': 'notes',
                                 'media_folder_name': 'attachments',
                                 'creation_time_in_exported_file_name': 'no'}

        def default_image_link_formats(self):
            # if you change this changes are likely in all places that call this method
            self.image_link_formats = {'    # valid entries are': None,
                                       '    # strict_md     which looks like [](path to image)': None,
                                       '    # gfm-html      which looks like <img src=path to file width=width_value>': None,
                                       '    # obsidian      which looks like [|width_value](path to image)': None,
                                       'image_link_format': 'strict_md'}

        def set_quick_set_settings(self, quick_set):
            quick_set_method_name = 'set_quick_settings_for_' + quick_set  # build method name
            func = getattr(self, quick_set_method_name)  # find method that located within the class
            func()  # execute the method

            return {'quick_settings': self.quick_settings, 'export_formats': self.export_formats,
                    'meta_data_options': self.meta_data_options, 'file_options': self.file_options,
                    'image_link_formats': self.image_link_formats}

        def set_quick_settings_for_manual(self):
            self.current_quick_set = 'manual'

        def set_quick_settings_for_q_own_notes(self):
            self.default_quick_settings()
            self.default_export_formats()
            self.default_meta_data_options()
            self.default_file_options()
            self.default_image_link_formats()
            self.current_quick_set = 'q_own_notes'
            self.export_formats = 'q_own_notes'
            self.image_link_formats['image_link_format'] = 'strict_md'

        def set_quick_settings_for_gfm(self):
            self.default_quick_settings()
            self.default_quick_settings()
            self.default_export_formats()
            self.default_meta_data_options()
            self.meta_data_options['yaml_meta_header_format'] = 'yes'
            self.default_file_options()
            self.image_link_formats['image_link_format'] = 'gfm-html'
            self.current_quick_set = 'gfm'

        def set_quick_settings_for_obsidian(self):
            self.default_quick_settings()
            self.default_export_formats()
            self.default_meta_data_options()
            self.meta_data_options['yaml_meta_header_format'] = 'yes'
            self.default_file_options()
            self.image_link_formats['image_link_format'] = 'obsidian'
            self.current_quick_set = 'obsidian'

        def set_quick_settings_for_pdf(self):
            self.default_quick_settings()
            self.default_meta_data_options()
            self.meta_data_options['include_meta_data'] = 'no'
            self.default_file_options()
            self.current_quick_set = 'pdf'

    #### old stuff below here

    def get_attachment_folder(self):
        return self.attachment_folder

    def get_output_folder(self):
        return self.output_folder


if __name__ == '__main__':
    # for testing
    my_config = ConfigData('config.ini', allow_no_value=True)
    # my_config.write_config_file()
    # my_config.default_config.set_quick_set_settings("gfm")
    # my_config.write_config_file()
    # my_config.read_config_file()
    print("Done")
