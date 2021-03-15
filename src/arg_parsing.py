import argparse
import os
from globals import VERSION
import quick_settings
import logging
import inspect
from globals import APP_NAME


def what_module_is_this():
    return __name__


def what_method_is_this():
    return inspect.currentframe().f_back.f_code.co_name


def what_class_is_this(obj):
    return obj.__class__.__name__


class CommandLineParsing:
    """
    Read command line arguments, and generate conversion settings based on these values

    """
    def __init__(self):
        self.logger = logging.getLogger(f'{APP_NAME}.{what_module_is_this()}.{what_class_is_this(self)}')
        self.logger.setLevel(logging.DEBUG)
        self._parser = argparse.ArgumentParser(description="YANOM Note-O-Matic notes convertor")
        self.__configure_parser()
        self.logger.info("Parsing command line arguments")
        self._args = self._parser.parse_args()
        self.logger.info(f"command line arguments are {self._args}")
        self._conversion_setting = quick_settings.please.provide('manual')
        self.__generate_conversion_settings()

    @property
    def conversion_setting(self):
        return self._conversion_setting

    @property
    def args(self):
        return vars(self._args)

    def __configure_parser(self):
        """Define the command line arguments"""

        self._parser.add_argument('-v', '--version', action='version', version='%(prog)s Version {}'.format(VERSION))
        self._parser.add_argument("-s", "--silent", action="store_true",
                                  help="No output to console. No interactive command line interface for settings.")
        self._parser.add_argument('--source', nargs='?', default=os.getcwd(),
                                  help='Sub directory of current directory containing one or more *.nsx files, '
                                       'or the name of a single nsx file.  '
                                       'For example "my_nsx_files" or "my_nsx_files/my_nsx_file.nsx".  '
                                       'If not provided will search and use current folder.')
        group = self._parser.add_argument_group('Mutually exclusive options. ',
                                                'To use the interactive command line tool for settings '
                                                'DO NOT use -s, -g, -i, -q, or -m')
        settings_from_group = group.add_mutually_exclusive_group()
        settings_from_group.add_argument("-g", "--gui", action="store_true", help="Use gui interface.")
        settings_from_group.add_argument("-i", "--ini", action="store_true",
                                         help="Use config.ini for conversion settings.")
        settings_from_group.add_argument('-q', "--quickset", choices=['q_own_notes', 'gfm', 'obsidian', 'pdf'],
                                         default='gfm',
                                         help="Choose a quick conversion setting")
        settings_from_group.add_argument('-m', "--manual", action="store_true",
                                         help="Use manual settings commandline options")

        manual_settings_group = self._parser.add_argument_group('Manual conversion settings options. Use with -m')

        meta_settings_group = self._parser.add_argument_group(
            title='Meta Data options.  Use with -m for manual settings')
        meta_settings_group.add_argument('--meta-data', action="store_true",
                                         help='Include meta data in output file. NOTE if not used the rest of the meta '
                                              'data options will NOT be used even if provided')
        meta_settings_group.add_argument('--yaml', action="store_true", help='Place meta data in a YAML header')
        meta_settings_group.add_argument('--title', action="store_true", help='Include note title in meta data')
        meta_settings_group.add_argument('--creation', action="store_true",
                                         help='Include note creation time in meta data')
        meta_settings_group.add_argument('--modified', action="store_true",
                                         help='Include note modified time in meta data')
        meta_settings_group.add_argument('--tags', action="store_true", help='Include note modified time in meta data')

        meta_settings_group.add_argument('--spaces', action="store_true", help='Allow spaces in tag name')
        meta_settings_group.add_argument('--split', action="store_true", help='Split tags')
        meta_settings_group.add_argument('--prefix', nargs='?', default='',
                                         help='Prefix to be applied to tag words. '
                                              'If not provided defaults to no prefix.')
        manual_settings_group.add_argument('--ctef', action="store_true",
                                           help='Add meta creation time to end of note filename')
        manual_settings_group.add_argument("--images", choices=['strict_md', 'obsidian', 'gfm-html'],
                                           default='strict_md',
                                           help="Choose image format for image links.  Default is strict_md."
                                                "Options are 'strict_md', 'obsidian', 'gfm-html'.")
        manual_settings_group.add_argument('-x', '--export-format', choices=['q_own_notes', 'gfm', 'obsidian', 'pdf'],
                                           default='gfm',
                                           help="Default is 'gfm'.  Options are "
                                                "q_own_notes=markdown-strict minus html plus pipe tables, "
                                                "gfm=git-flavoured markdown, "
                                                "obsidian=git-flavoured markdown, "
                                                "pdf=pdf file and attachments as separate files.")
        self._parser.add_argument('--export-folder', nargs='?', default='notes',
                                  help='If not provided defaults to "notes".  This is the name of sub folder to place '
                                       'exported notebooks into.  If a source folder has been provided the notes '
                                       'folder will be created in that folder. If no source is provided the notes '
                                       'folder will be created in the current folder.')
        self._parser.add_argument('--attachments', nargs='?', default='attachments',
                                  help='Name of sub folder to create, inside of the notebook folders to store images '
                                       'and attachments.  Default=attachments')

    def __generate_conversion_settings(self):
        """Transcribe command line arguments into ConversionSettings object"""

        self.logger.info("Generating conversion settings based on command line arguments")
        self.conversion_setting.quick_setting = vars(self._args)['quickset']
        self.conversion_setting.export_format = vars(self._args)['export_format']
        self.conversion_setting.include_meta_data = vars(self._args)['meta_data']
        self.conversion_setting.yaml_meta_header_format = vars(self._args)['yaml']
        self.conversion_setting.insert_title = vars(self._args)['title']
        self.conversion_setting.insert_creation_time = vars(self._args)['creation']
        self.conversion_setting.insert_modified_time = vars(self._args)['modified']
        self.conversion_setting.include_tags = vars(self._args)['tags']
        self.conversion_setting.tag_prefix = vars(self._args)['prefix']
        self.conversion_setting.spaces_in_tags = vars(self._args)['spaces']
        self.conversion_setting.split_tags = vars(self._args)['split']
        self.conversion_setting.source = vars(self._args)['source']
        self.conversion_setting.export_folder_name = vars(self._args)['export_folder']
        self.conversion_setting.attachment_folder_name = vars(self._args)['attachments']
        self.conversion_setting.creation_time_in_exported_file_name = vars(self._args)['ctef']
        self.conversion_setting.image_link_format = vars(self._args)['images']


if __name__ == '__main__':
    args = CommandLineParsing()
    print(args.args)
    print(args.conversion_setting)
