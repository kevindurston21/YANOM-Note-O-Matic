"""
Provide classes for provision of conversion settings for manual or specific pre configured sets of conversion settings

"""
import object_factory
from abc import ABC, abstractmethod
from globals import APP_NAME
import inspect
import logging
from helper_functions import generate_clean_path
from custom_inherit import DocInheritMeta
import os
from pathlib import Path
import sys


def what_module_is_this():
    return __name__


def what_method_is_this():
    return inspect.currentframe().f_back.f_code.co_name


def what_class_is_this(obj):
    return obj.__class__.__name__


class ConversionSettingsError(Exception):
    pass


class ConversionSettingProvider(object_factory.ObjectFactory):
    """
    ConversionSettingProvider generator

    Used to generate configuration settings for specific 'quick settings' or a manual setting where the user selects
    all options, manual is also used by the ConfigData class to pass settings from a config.ini file

    Yields
    ------
    Child of ConversionSettings
        Requested child object is generated based on request string value.

    """

    def provide(self, conversion_setting_type, **_ignored):
        return self.create(conversion_setting_type)


class ConversionSettings(metaclass=DocInheritMeta(style="numpy", abstract_base_class=True)):
    """
    Conversion settings required to convert input formats to export formats.

    Child classes implement specific 'quick settings' for pre-known typical formats for files or notes programs,
    or a user configured conversion setting where a quick setting does not meet a required need.

    Attributes
    ----------
    validation_values : dict
        a static dictionary that is used by ConfigData class to validate ini files read from disk.
    logger : logger object
        used for program logging
    _valid_quick_settings : list
        Quick settings strings that are used to create 'default' conversions for various program and file types.
        Also are the values used in an object generator to create child classes
    _valid_export_formats : list
        Export format names used to trigger specific conversion behaviour in style of file type
    _valid_image_link_formats: list
        Image link formats used in markdown files to style image links for display
    _silent : bool
        Run program with no output to command line
    _source : pathlib.Path
        Directory to search for nsx files or path to specific nsx file
    _quick_setting: str
        A trigger string used for a default set for some of the following filed values
    _export_format: str
        The export format to be used
    _include_meta_data: bool
        Add available meta data, not in a note body, to the main text of the exported note
    _yaml_meta_header_format: bool
        Meta data to be placed in a yaml header above the body of the main text
    _insert_title: bool
        Include title in the included meta data
    _insert_creation_time: bool
        Include the note creation time in the included meta data
    _insert_modified_time: bool
        Include the note modified time iin the included meta data
    _include_tags: bool
        Include tags in the meta data
    _tag_prefix: str
        Prefix to place on tags
    _spaces_in_tags: bool
        Allow spaces in tag names
    _split_tags: bool
        Split tags into separate tags where the input was a grouped tag format e.g. /coding/python -> coding python
    _export_folder_name: pathlib.Path
        Path object for the sub-directory name to place exported notes into
    _attachment_folder_name: pathlib.Path
        Path object for the sub-directory name within the export folder to place images and attachments
    _creation_time_in_exported_file_name: bool
        Include the note creation time on the end of the file name
    _image_link_format : str
            Image link styling to be used in markdown files

    Methods
    -------
    set_settings()
        Change attribute values to achieve a specific conversion process

    """
    validation_values = {
        'execution_mode': {
            'silent': ('True', 'False')
        },
        'quick_settings': {
            'quick_setting': ('manual', 'q_own_notes', 'obsidian', 'gfm', 'pdf')
        },
        'export_formats': {
            'export_format': ('q_own_notes', 'obsidian', 'gfm', 'pdf')
        },
        'meta_data_options': {
            'include_meta_data': ('True', 'False'),
            'yaml_meta_header_format': ('True', 'False'),
            'insert_title': ('True', 'False'),
            'insert_creation_time': ('True', 'False'),
            'insert_modified_time': ('True', 'False'),
            'include_tags': ('True', 'False'),
            'tag_prefix': '',
            'spaces_in_tags': ('True', 'False'),
            'split_tags': ('True', 'False')
        },
        'file_options': {
            'source': '',
            'export_folder_name': '',
            'attachment_folder_name': '',
            'creation_time_in_exported_file_name': ('True', 'False')
        },
        'image_link_formats': {'image_link_format': ('strict_md', 'obsidian', 'gfm-html')}
    }

    def __init__(self, **kwargs):
        # Note #comments are treated as 'values' with no value in a config.ini.
        # So to get the comment into the ini use a dictionary entry
        # where the key value pair are like this '#your comment': None
        # the #comments in these dicts are only there to add comments to the config.ini

        # if you change anr of the following dictionaries changes are likely to affect the quick settings child classes
        # and the ConfigFileValidationSettings class
        # self.output_file_types = ['md', 'pdf']
        self.logger = logging.getLogger(f'{APP_NAME}.{what_module_is_this()}.{what_class_is_this(self)}')
        self.logger.setLevel(logging.DEBUG)
        self._valid_quick_settings = list(self.validation_values['quick_settings']['quick_setting'])
        self._valid_export_formats = list(self.validation_values['export_formats']['export_format'])
        self._valid_image_link_formats = list(self.validation_values['image_link_formats']['image_link_format'])
        self._silent = False
        self._source = os.getcwd()
        self._quick_setting = 'gfm'
        self._export_format = 'gfm'
        self._include_meta_data = True
        self._yaml_meta_header_format = False
        self._insert_title = True
        self._insert_creation_time = True
        self._insert_modified_time = True
        self._include_tags = True
        self._tag_prefix = '#'
        self._spaces_in_tags = False
        self._split_tags = False
        self._export_folder_name = 'notes'
        self._attachment_folder_name = 'attachments'
        self._creation_time_in_exported_file_name = False
        self._image_link_format = 'strict_md'

        self.set_settings()

    def __str__(self):
        return f"{self.__class__.__name__}(silent={self.silent}, quick_setting='{self.quick_setting}', " \
               f"export_format='{self.export_format}', include_meta_data={self.include_meta_data}, " \
               f"yaml_header={self.yaml_meta_header_format}, insert_title={self.insert_title}, " \
               f"insert_creation_time={self.insert_creation_time}, insert_modified_time={self.insert_modified_time}, " \
               f"include_tags={self.include_tags}, tag_prefix='{self.tag_prefix}', " \
               f"spaces_in_tags={self.spaces_in_tags}, split_tags={self.split_tags}, " \
               f"export_folder_name='{self.export_folder_name}', " \
               f"attachment_folder_name='{self.attachment_folder_name}', " \
               f"creation_time_in_exported_file_name={self.creation_time_in_exported_file_name}, " \
               f"image_link_format='{self.image_link_format}')"

    def __repr__(self):
        return f"{self.__class__.__name__}(silent={self.silent}, quick_setting='{self.quick_setting}', " \
               f"export_format='{self.export_format}', include_meta_data={self.include_meta_data}, " \
               f"yaml_header={self.yaml_meta_header_format}, insert_title={self.insert_title}, " \
               f"insert_creation_time={self.insert_creation_time}, insert_modified_time={self.insert_modified_time}, " \
               f"include_tags={self.include_tags}, tag_prefix='{self.tag_prefix}', " \
               f"spaces_in_tags={self.spaces_in_tags}, split_tags={self.split_tags}, " \
               f"export_folder_name='{self.export_folder_name}', " \
               f"attachment_folder_name='{self.attachment_folder_name}', " \
               f"creation_time_in_exported_file_name={self.creation_time_in_exported_file_name}, " \
               f"image_link_format='{self.image_link_format}')"

    @abstractmethod
    def set_settings(self):
        pass

    @property
    def valid_quick_settings(self):
        return self._valid_quick_settings

    @property
    def valid_export_formats(self):
        return self._valid_export_formats

    @property
    def valid_image_link_formats(self):
        return self._valid_image_link_formats

    @property
    def silent(self):
        return self._silent

    @silent.setter
    def silent(self, value: bool):
        self._silent = value

    @property
    def source(self):
        return self._source

    @source.setter
    def source(self, value):
        if value == '':
            self._source = Path(os.getcwd())
        elif Path(value).exists():
            self._source = Path(value)
        else:
            self.logger.error(f"Invalid source location - {value} - Exiting program")
            if not self.silent:
                print(f"Invalid source location - {value}")
            raise ConversionSettingsError(f"Invalid source location - {value}")

    @property
    def quick_setting(self):
        return self._quick_setting

    @quick_setting.setter
    def quick_setting(self, value):
        if value in self.valid_quick_settings:
            self._quick_setting = value
        else:
            raise ValueError(f"Invalid value for quick setting. "
                             f"Attempted to use {value}, valid values are {self.valid_quick_settings}")

    @property
    def export_format(self):
        return self._export_format

    @export_format.setter
    def export_format(self, value):
        if value in self.valid_export_formats:
            self._export_format = value
        else:
            raise ValueError(f"Invalid value for export format. "
                             f"Attempted to use {value}, valid values are {self.valid_export_formats}")

    @property
    def include_meta_data(self):
        return self._include_meta_data

    @include_meta_data.setter
    def include_meta_data(self, value: bool):
        self._include_meta_data = value

    @property
    def yaml_meta_header_format(self):
        return self._yaml_meta_header_format

    @yaml_meta_header_format.setter
    def yaml_meta_header_format(self, value: bool):
        self._yaml_meta_header_format = value

    @property
    def insert_title(self):
        return self._insert_title

    @insert_title.setter
    def insert_title(self, value: bool):
        self._insert_title = value

    @property
    def insert_creation_time(self):
        return self._insert_creation_time

    @insert_creation_time.setter
    def insert_creation_time(self, value: bool):
        self._insert_creation_time = value

    @property
    def insert_modified_time(self):
        return self._insert_modified_time

    @insert_modified_time.setter
    def insert_modified_time(self, value: bool):
        self._insert_modified_time = value

    @property
    def include_tags(self):
        return self._include_tags

    @include_tags.setter
    def include_tags(self, value: bool):
        self._include_tags = value

    @property
    def tag_prefix(self):
        return self._tag_prefix

    @tag_prefix.setter
    def tag_prefix(self, value: str):
        self._tag_prefix = value

    @property
    def spaces_in_tags(self):
        return self._spaces_in_tags

    @spaces_in_tags.setter
    def spaces_in_tags(self, value: bool):
        self._spaces_in_tags = value

    @property
    def split_tags(self):
        return self._split_tags

    @split_tags.setter
    def split_tags(self, value: bool):
        self._split_tags = value

    @property
    def export_folder_name(self):
        return self._export_folder_name

    @export_folder_name.setter
    def export_folder_name(self, value):
        self._export_folder_name = generate_clean_path(value)

    @property
    def attachment_folder_name(self):
        return self._attachment_folder_name

    @attachment_folder_name.setter
    def attachment_folder_name(self, value):
        self._attachment_folder_name = generate_clean_path(value)

    @property
    def creation_time_in_exported_file_name(self):
        return self._creation_time_in_exported_file_name

    @creation_time_in_exported_file_name.setter
    def creation_time_in_exported_file_name(self, value: bool):
        self._creation_time_in_exported_file_name = value

    @property
    def image_link_format(self):
        return self._image_link_format

    @image_link_format.setter
    def image_link_format(self, value: str):
        if value in self.valid_image_link_formats:
            self._image_link_format = value
        else:
            raise ValueError(f"Invalid value for export format. "
                             f"Attempted to use {value}, valid values are {self.valid_image_link_formats}")


class ManualConversionSettings(ConversionSettings):
    """
    Manual conversion settings to convert input formats to export formats.

    Used for user configured selections and ConfigData Class to provide conversions read from ini files.
    """

    def set_settings(self):
        """Set initial conversion settings for a manual conversion setting"""
        self.logger.info("Manual conversion settings")
        self.quick_setting = 'manual'
        self.yaml_meta_header_format = False
        self.insert_title = False
        self.insert_creation_time = False
        self.insert_modified_time = False
        self.include_tags = False
        self.spaces_in_tags = False
        self.split_tags = False


class QOwnNotesConversionSettings(ConversionSettings):
    """
    QOwnNotes conversion settings to convert input formats to format suitable for QOwnNotes users.
    """

    def set_settings(self):
        self.logger.info("QOwnNotes Setting conversion settings")
        self.quick_setting = 'q_own_notes'
        self.export_format = 'q_own_notes'
        self.image_link_format = 'strict_md'


class GfmConversionSettings(ConversionSettings):
    """
    Git-flavoured markdown conversion settings to convert input formats to gfm format.
    """

    def set_settings(self):
        self.logger.info("GFM conversion settings")
        self.quick_setting = 'gfm'
        self.yaml_meta_header_format = True
        self.image_link_format = 'gfm-html'


class ObsidianConversionSettings(ConversionSettings):
    """
    Obsidian conversion settings to convert input formats to format suitable for Obsidian users.
    """

    def set_settings(self):
        self.logger.info("Obsidian conversion settings")
        self.quick_setting = 'obsidian'
        self.yaml_meta_header_format = True
        self.image_link_format = 'obsidian'


class PdfConversionSettings(ConversionSettings):
    """
    PDF conversion settings to convert input formats to pdf files plus attachments in a folder.
    """

    def set_settings(self):
        self.logger.info("PDF conversion settings")
        self.export_format = 'pdf'
        self.include_meta_data = False


please = ConversionSettingProvider()
please.register_builder('manual', ManualConversionSettings)
please.register_builder('q_own_notes', QOwnNotesConversionSettings)
please.register_builder('gfm', GfmConversionSettings)
please.register_builder('obsidian', ObsidianConversionSettings)
please.register_builder('pdf', PdfConversionSettings)





