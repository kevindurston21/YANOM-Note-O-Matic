from PyInquirer import style_from_dict, Token, prompt, Separator
from abc import ABC, abstractmethod
import quick_settings
from quick_settings import ManualConversionSettings
from pyfiglet import Figlet
from globals import APP_NAME, APP_SUB_NAME
import logging
import inspect


def what_module_is_this():
    return __name__


def what_method_is_this():
    return inspect.currentframe().f_back.f_code.co_name


def what_class_is_this(obj):
    return obj.__class__.__name__


def show_app_title():
    print(Figlet().renderText(APP_NAME))
    f = Figlet(font='slant')
    print(f.renderText(APP_SUB_NAME))


class InquireCommandLineInterface(ABC):
    """
    Abstract class to define a consistent style format for child classes

    Methods
    -------
    run_cli:
        This abstract method should be the only public method in child classes and will execute methods required to
        ask for input, process responses as required and return required values.
    """
    def __init__(self):
        self.style = style_from_dict({
            Token.Separator: '#cc5454',
            Token.QuestionMark: '#673ab7 bold',
            Token.Selected: '#cc5454',  # default
            Token.Pointer: '#673ab7 bold',
            Token.Instruction: '',  # default
            Token.Answer: '#f44336 bold',
            Token.Question: '',
        })

    @abstractmethod
    def run_cli(self):
        pass


class StartUpCommandLineInterface(InquireCommandLineInterface):
    """
    Command line interface to run on program stratup.

    Returns a configured child of ConversionSettings class
    """
    def __init__(self, config_ini_conversion_settings):
        super(StartUpCommandLineInterface, self).__init__()
        self.logger = logging.getLogger(f'{APP_NAME}.{what_module_is_this()}.{what_class_is_this(self)}')
        self.logger.setLevel(logging.DEBUG)
        self._default_settings = config_ini_conversion_settings
        self._current_conversion_settings = None

    def run_cli(self):
        self.logger.info("Running start up interactive command line")
        show_app_title()

        self.__ask_and_set_conversion_quick_setting()

        if type(self._current_conversion_settings) is ManualConversionSettings:
            self.__ask_and_set_export_format()
            include = self.__ask_and_set_include_metadata()
            if include:
                self.__ask_and_set_metadata_details()
                self.__ask_and_set_tag_prefix()
            self.__ask_and_set_table_details()
            self.__ask_and_set_export_folder_name()
            self.__ask_and_set_attachment_folder_name()
            self.__ask_and_set_creation_time_in_file_name()
            self.__ask_and_set_image_link_formats()
            self.logger.info(f"Returning Manual settings of {self._current_conversion_settings}")
            return self._current_conversion_settings

        self.logger.info(f"Returning Quick settings for {self._current_conversion_settings.quick_setting}")
        return self._current_conversion_settings

    def __ask_and_set_conversion_quick_setting(self):
        # ordered_list puts current default into the top of the list, this is needed because the default option on lists
        # in PyInquirer does not work
        ordered_list = self._default_settings.valid_quick_settings.copy()
        ordered_list.insert(0, ordered_list.pop(ordered_list.index(self._default_settings.quick_setting)))
        quick_setting_prompt = {
            'type': 'list',
            'name': 'quick_setting',
            'message': 'Choose a quick setting or manual mode',
            'choices': ordered_list
        }
        answer = prompt(quick_setting_prompt, style=self.style)
        self._current_conversion_settings = quick_settings.please.provide(answer['quick_setting'])

    def __ask_and_set_export_format(self):
        # ordered_list puts current default into the top of the list, this is needed because the default option on lists
        # in PyInquirer does not work
        ordered_list = self._default_settings.valid_export_formats.copy()
        ordered_list.insert(0, ordered_list.pop(ordered_list.index(self._default_settings.export_format)))
        export_format_prompt = {
            'type': 'list',
            'name': 'export_format',
            'message': 'Choose an export format',
            'choices': ordered_list

        }
        answer = prompt(export_format_prompt, style=self.style)
        self._current_conversion_settings.export_format = answer['export_format']

    def __ask_and_set_include_metadata(self):
        questions = [
            {
                'type': 'confirm',
                'message': 'Do you want to include meta data?',
                'name': 'include_meta_data',
                'default': self._default_settings.include_meta_data,
            },
        ]

        answer = prompt(questions, style=self.style)
        self._current_conversion_settings.include_meta_data = answer['include_meta_data']

        return answer['include_meta_data']

    def __ask_and_set_metadata_details(self):
        questions = [
            {
                'type': 'checkbox',
                'message': 'Select meta data details',
                'name': 'metadata_details',
                'choices': [
                    Separator('= Use YAML header ='),
                    {
                        'name': 'YAML header',
                        'checked': self._default_settings.yaml_meta_header_format
                    },
                    Separator('= Note Details ='),
                    {
                        'name': 'Title included',
                        'checked': self._default_settings.insert_title
                    },
                    {
                        'name': 'Creation time included',
                        'checked': self._default_settings.insert_creation_time
                    },
                    {
                        'name': 'Modified time included',
                        'checked': self._default_settings.insert_modified_time
                    },
                    Separator('= Tag options ='),
                    {
                        'name': 'Tags included',
                        'checked': self._default_settings.include_tags
                    },
                    {
                        'name': 'Spaces in tags',
                        'checked': self._default_settings.spaces_in_tags
                    },
                    {
                        'name': 'Split tags',
                        'checked': self._default_settings.split_tags
                    },
                ],
            }
        ]

        answers = prompt(questions, style=self.style)

        if 'YAML header' in answers['metadata_details']:
            self._current_conversion_settings.yaml_meta_header_format = True

        if 'Title included' in answers['metadata_details']:
            self._current_conversion_settings.insert_title = True

        if 'Creation time included' in answers['metadata_details']:
            self._current_conversion_settings.insert_creation_time = True

        if 'Modified time included' in answers['metadata_details']:
            self._current_conversion_settings.insert_modified_time = True

        if 'Tags included' in answers['metadata_details']:
            self._current_conversion_settings.include_tags = True

        if 'Spaces in tags' in answers['metadata_details']:
            self._current_conversion_settings.spaces_in_tags = True

        if 'Split tags' in answers['metadata_details']:
            self._current_conversion_settings.split_tags = True

    def __ask_and_set_table_details(self):
        questions = [
            {
                'type': 'checkbox',
                'message': 'Select table options',
                'name': 'table_options',
                'choices': [
                    Separator('= Table Options ='),
                    {
                        'name': 'First row of table as header row',
                        'checked': self._default_settings.first_row_as_header
                    },
                    {
                        'name': 'First column of table as header column',
                        'checked': self._default_settings.first_column_as_header
                    },

                ],
            }
        ]

        answers = prompt(questions, style=self.style)

        if 'First row of table as header row' in answers['table_options']:
            self._current_conversion_settings.first_row_as_header = True

        if 'First column of table as header column' in answers['table_options']:
            self._current_conversion_settings.first_column_as_header = True


    def __ask_and_set_tag_prefix(self):
        questions = [
            {
                'type': 'input',
                'name': 'tag_prefix',
                'message': 'Enter a tag prefix e.g. # or @',
                'default': self._default_settings.tag_prefix
            },
        ]

        answer = prompt(questions, style=self.style)
        self._current_conversion_settings.tag_prefix = answer['tag_prefix']

    def __ask_and_set_export_folder_name(self):
        questions = [
            {
                'type': 'input',
                'name': 'export_folder_name',
                'message': 'Enter a directory name for notes to be exported to',
                'default': str(self._default_settings.export_folder_name)
            },
        ]
        answers = prompt(questions, style=self.style)
        self._current_conversion_settings.export_folder_name = answers['export_folder_name']
        if str(self._current_conversion_settings.export_folder_name) != answers['export_folder_name']:
            self.__ask_to_confirm_changed_path_name(self._current_conversion_settings.export_folder_name)

    def __ask_and_set_attachment_folder_name(self):
        questions = [
            {
                'type': 'input',
                'name': 'attachment_folder_name',
                'message': 'Enter a directory name for notes to be exported to',
                'default': str(self._default_settings.attachment_folder_name)
            },
        ]
        answers = prompt(questions, style=self.style)
        self._current_conversion_settings.attachment_folder_name = answers['attachment_folder_name']
        if str(self._current_conversion_settings.attachment_folder_name) != answers['attachment_folder_name']:
            self.__ask_to_confirm_changed_path_name(self._current_conversion_settings.attachment_folder_name)

    def __ask_to_confirm_changed_path_name(self, new_path):
        message = f"Your submitted folder name has been changed to {new_path}. Do you accept this change?"
        questions = [
            {
                'type': 'confirm',
                'message': message,
                'name': 'accept_change',
                'default': True,
            },
        ]

        answer = prompt(questions, style=self.style)
        if not answer['accept_change']:
            self.__ask_and_set_export_folder_name()

    def __ask_and_set_creation_time_in_file_name(self):
        questions = [
            {
                'type': 'confirm',
                'message': 'Include creation time in the file name',
                'name': 'creation_time_in_exported_file_name',
                'default': self._default_settings.creation_time_in_exported_file_name,
            },
        ]

        answers = prompt(questions, style=self.style)
        self._current_conversion_settings.creation_time_in_exported_file_name = answers[
            'creation_time_in_exported_file_name']

    def __ask_and_set_image_link_formats(self):
        # ordered_list puts current default into the top of the list, this is needed because the default option on lists
        # in PyInquirer does not work
        ordered_list = self._default_settings.valid_image_link_formats.copy()
        ordered_list.insert(0, ordered_list.pop(ordered_list.index(self._default_settings.image_link_format)))
        export_format_prompt = {
            'type': 'list',
            'name': 'image_link_format',
            'message': 'Choose an image link format',
            'choices': ordered_list
        }
        answer = prompt(export_format_prompt, style=self.style)
        self._current_conversion_settings.image_link_format = answer['image_link_format']


class InvalidConfigFileCommandLineInterface(InquireCommandLineInterface):
    """
    Command Line Interface for errors when validating an imported config.ini file
    """

    def __init__(self):
        super().__init__()

    def run_cli(self):
        return self.__ask_what_to_do()

    def __ask_what_to_do(self):
        question = {
            'type': 'list',
            'name': 'what_to_do',
            'message': 'Config file is invalid, please make a choice',
            'choices': ['Create a default configuration', 'Exit program and edit config file']
        }

        answer = prompt(question, style=self.style)
        if answer['what_to_do'] == 'Create a default configuration':
            return 'default'
        return 'exit'


if __name__ == '__main__':
    cli = StartUpCommandLineInterface(quick_settings.please.provide('obsidian'))
    cli.run_cli()
