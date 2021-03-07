from configparser import ConfigParser
from pathlib import Path
from quick_settings import ConversionSettings
import quick_settings
import logging
import inspect
from globals import APP_NAME
from interactive_cli import InvalidConfigFileCommandLineInterface
import sys


def what_module_is_this():
    return __name__


def what_method_is_this():
    return inspect.currentframe().f_back.f_code.co_name


def what_class_is_this(obj):
    return obj.__class__.__name__


class ConfigException(Exception):
    pass


class ConfigData(ConfigParser):
    """
    Read, verify, update and write config.ini files

    Attributes
    ----------
    logger : logging object
        used for program logging
    config_file : str
        name of the configuration file to be parsed and to use for storing config data
    default_quick_setting :  str
        setting to be used if the config.ini is found to be invalid and uses chooses to use the default
    conversion_settings :  Child of ConversionSettings, holds config data in a format to be used outside of the class
    validation_values :  dict
        holds the values required to validate a config file read from disk

    """

    def __init__(self, config_file, default_quick_setting, **kwargs):
        super(ConfigData, self).__init__(**kwargs)
        # Note: allow_no_value=True  allows for #comments in the ini file
        self.logger = logging.getLogger(f'{APP_NAME}.{what_module_is_this()}.{what_class_is_this(self)}')
        self.logger.setLevel(logging.DEBUG)
        self._config_file = config_file
        self._default_quick_setting = default_quick_setting
        self._conversion_settings = quick_settings.please.provide('manual')
        self._validation_values = self._conversion_settings.validation_values
        self.__read_config_file()
        self.__validate_config_file()
        self.__generate_conversion_settings_from_parsed_config_file_data()
        self.logger.info(f"Settings from config.ini are {self._conversion_settings}")

    @property
    def conversion_settings(self):
        return self._conversion_settings

    @conversion_settings.setter
    def conversion_settings(self, value):
        """
        Receive a conversion setting as a quick setting string of a ConversionSettings object,
        set the _conversion_setting, generate and save config ini file for the setting received.

        Parameters
        ----------
        value : str or ConversionSettings
            If str must be a valid quick_setting string value.

        """
        if type(value) is str:
            if value in self._conversion_settings.valid_quick_settings:
                self.load_config_from_conversion_quick_setting_string(value)
                return
            self.logger.error(f"Passed invalid value - {value} - not a recognised quick setting string")
            raise ValueError(f"Conversion setting parameter must be a valid quick setting string "
                             f"{self._conversion_settings.valid_quick_settings} received '{value}'")
        if type(value) is ConversionSettings:
            self.load_config_from_conversion_settings_obj(value)
            return
        self.logger.error(f"Passed invalid value - {value}")
        raise TypeError(f"Conversion setting parameter must be a valid quick setting "
                        f"{self._conversion_settings.valid_quick_settings} string or a ConversionSettings object")

    def __validate_config_file(self):
        """
        Validate config data.  Errors in the data prompt user to create a new default configuration or exit the program

        """
        self.logger.debug("attempting to validate config file")
        try:
            self.__validate_config()
            self.logger.info("config file validated")
        except ConfigException as e:
            self.logger.warning(f"Config file invalid \n{e}")

            ask_what_to_do = InvalidConfigFileCommandLineInterface()
            what_to_do = ask_what_to_do.run_cli()
            if what_to_do == 'exit':
                sys.exit(0)
            self.logger.info("User chose to create default file")
            self.load_config_from_conversion_quick_setting_string(self._default_quick_setting)
            self._load_settings()

    def __validate_config(self):
        """
        Validate the current Config Data for any errors by comparing to a set of validation values.

        Errors will raise a ConfigException

        """
        for section, keys in self._validation_values.items():
            if section not in self:
                raise ConfigException(f'Missing section {section} in the config ini file')

            for key, values in keys.items():
                if key not in self[section] or self[section][key] == '':
                    raise ConfigException(f'Missing value for {key} under section {section} in the config ini file')

                if values:
                    if self[section][key] not in values:
                        raise ConfigException(f'Invalid value for {key} under section {section} in the config file')

    def __generate_conversion_settings_from_parsed_config_file_data(self):
        """
        Transcribe the values in a ConversionSettings object into the ConfigParser format used by this class

        """
        self._conversion_settings.silent = self['execution_mode']['silent']
        self._conversion_settings.quick_setting = self['quick_settings']['quick_setting']
        self._conversion_settings.export_format = self['export_formats']['export_format']
        self._conversion_settings.include_meta_data = self['meta_data_options']['include_meta_data']
        self._conversion_settings.yaml_meta_header_format = self['meta_data_options']['yaml_meta_header_format']
        self._conversion_settings.insert_title = self['meta_data_options']['insert_title']
        self._conversion_settings.insert_creation_time = self['meta_data_options']['insert_creation_time']
        self._conversion_settings.insert_modified_time = self['meta_data_options']['insert_modified_time']
        self._conversion_settings.include_tags = self['meta_data_options']['include_tags']
        self._conversion_settings.tag_prefix = self['meta_data_options']['tag_prefix']
        self._conversion_settings.spaces_in_tags = self['meta_data_options']['spaces_in_tags']
        self._conversion_settings.split_tags = self['meta_data_options']['split_tags']
        self._conversion_settings.export_folder_name = self['file_options']['export_folder_name']
        self._conversion_settings.attachment_folder_name = self['file_options']['attachment_folder_name']
        self._conversion_settings.creation_time_in_exported_file_name = \
            self['file_options']['creation_time_in_exported_file_name']
        self._conversion_settings.image_link_format = self['image_link_formats']['image_link_format']

    def __write_config_file(self):
        with open(self._config_file, 'w') as config_file:
            self.write(config_file)
            self.logger.info("Saving configuration file")

    def __read_config_file(self):
        """
        Read config file. If file is missing generate a new one.

        If config file is missing generate a ConversionSettings child object for the default conversion value
        and use that to generate a config data set.

        """
        self.logger.debug('reading config file')
        path = Path(self._config_file)
        if path.is_file():
            self.read(self._config_file)
        else:
            self.logger.info('config.ini missing, generating new file and settings set to default.')
            if not self.conversion_settings.silent:
                print("config.ini missing, generating new file.")
            self.conversion_settings = self._default_quick_setting

    def load_config_from_conversion_quick_setting_string(self, setting):
        """
        Generate a config data set and save the updated config file using a 'setting' value provided as a string
        that uses a default configuration by generating a child class of ConversionSettings and using that object
        to set the config values.

        Parameters
        ----------
        setting
            string: A key 'quick setting' value

        """
        self._conversion_settings = quick_settings.please.provide(setting)
        self.__load_and_save_settings()

    def load_config_from_conversion_settings_obj(self, settings: ConversionSettings):
        """
        Generate a config data set and save updtaed config file
        Parameters
        ----------
        settings
            ConversionSettings: A child of the class ConversionSettings

        """
        self._conversion_settings = settings
        self.__load_and_save_settings()

    def __load_and_save_settings(self):
        """
        Read a dictionary of config data, formatted for config file generation and store the new config file.

        """
        self.read_dict(self.__generate_conversion_dict())
        self.logger.info(f"Quick setting {self['quick_settings']['quick_setting']} loaded")
        self.__write_config_file()

    def __generate_conversion_dict(self):
        """

        Returns
        -------
        Dict
            Dictionary, formatted for config file creation, using values from a ConversionSettings object

        """
        # comments are treated as 'values' with no value (value is set to None) i.e. they are dict entries
        # where the key is the #comment string and the value is None
        return {
            'execution_mode': {
                '    # silent mode stops any output to the command line during execution': None,
                '    # and disables the interactive command line interface.': None,
                'silent': False
            },
            'quick_settings': {
                f'    # Valid entries are {", ".join(self._conversion_settings.valid_export_formats)}': None,
                '    # use manual to use manual settings below': None,
                '    # NOTE if an option other than - manual - is used the rest of the ': None,
                '    # settings in this file will be set automatically': None,
                '    #': None,
                "quick_setting": self._conversion_settings.quick_setting,
                '    # ': None,
                '    # The following sections only apply if all of the above are no': None,
                '    #  ': None
            },
            'export_formats': {
                f'    # Valid entries are {", ".join(self._conversion_settings.valid_export_formats)}': None,
                "export_format": self._conversion_settings.export_format
            },
            'meta_data_options': {
                'include_meta_data': self._conversion_settings.include_meta_data,
                '    # Note if include_meta_data = no then the following values will': None,
                '    # not be included in the export file': None,
                'yaml_meta_header_format': self._conversion_settings.yaml_meta_header_format,
                'insert_title': self._conversion_settings.insert_title,
                'insert_creation_time': self._conversion_settings.insert_creation_time,
                'insert_modified_time': self._conversion_settings.insert_modified_time,
                'include_tags': self._conversion_settings.include_tags,
                'tag_prefix': self._conversion_settings.tag_prefix,
                'spaces_in_tags': self._conversion_settings.spaces_in_tags,
                'split_tags': self._conversion_settings.split_tags
            },
            'file_options': {
                'source': self._conversion_settings.source,
                'export_folder_name': self._conversion_settings.export_folder_name,
                'attachment_folder_name': self._conversion_settings.attachment_folder_name,
                'creation_time_in_exported_file_name': self._conversion_settings.creation_time_in_exported_file_name
            },
            'image_link_formats': {
                '    # valid entries are': None,
                '    # strict_md     which looks like [](path to image)': None,
                '    # gfm-html      which looks like <img src=path to file width=width_value>': None,
                '    # obsidian      which looks like [|width_value](path to image)': None,
                'image_link_format': self._conversion_settings.image_link_format
            }
        }


if __name__ == '__main__':
    # for testing
    my_config = ConfigData('config.ini', 'gfm', allow_no_value=True)
    # my_config.conversion_settings = 'test.py'
    # my_config.conversion_settings = True
    # my_config.write_config_file()
    # my_config.default_config.set_quick_set_settings("gfm")
    # my_config.write_config_file()
    # my_config.read_config_file()
    print("Done")
