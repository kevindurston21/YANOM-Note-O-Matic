import shutil
import subprocess
import distutils.version
import os
import tempfile
import logging
from globals import APP_NAME
from pathlib import Path
import inspect


def what_module_is_this():
    return __name__


def what_method_is_this():
    return inspect.currentframe().f_back.f_code.co_name


def what_class_is_this(obj):
    return obj.__class__.__name__


def check_pandoc_is_installed_if_not_exit_program():
    if not shutil.which('pandoc') and not os.path.isfile('pandoc'):
        logging.info("Pandoc program not found - exiting")
        print("Can't find pandoc. Please install pandoc or place it to the directory, where the script is.")
        exit(1)


def error_handling(note_title):
    msg = f"Error converting note {note_title} for pandoc please check nsx_converter.log and pandoc installation."
    logging.error(msg)
    print(msg)
    print("Attempting to continue...")


def create_temporary_files():
    output_file = tempfile.NamedTemporaryFile(delete=False)
    input_file = tempfile.NamedTemporaryFile(delete=False)
    return output_file, input_file


class PandocConverter:
    def __init__(self, output_file_format):
        self.logger = logging.getLogger(f'{APP_NAME}.{what_module_is_this()}.{what_class_is_this(self)}')
        self.logger.setLevel(logging.DEBUG)
        self.output_file_format = output_file_format
        self.pandoc_version = None
        self.conversion_options = {'q_own_notes': 'markdown_strict+pipe_tables-raw_html',
                                   'gfm': 'gfm',
                                   'obsidian': 'gfm',
                                   'pdf': 'pdf'}
        self.pandoc_options = None
        check_pandoc_is_installed_if_not_exit_program()
        self.find_pandoc_version()
        self.generate_pandoc_options()

    def find_pandoc_version(self):
        try:
            self.pandoc_version = subprocess.run(['pandoc', '-v'], capture_output=True, text=True, timeout=3)
            self.pandoc_version = self.pandoc_version.stdout[7:].split('\n', 1)[0].strip()
            print('Found pandoc ' + str(self.pandoc_version))
            self.logger.info(f"Found pandoc version {str(self.pandoc_version)}")
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Exiting as unable to find pandoc\n{e}")
            print("Error testing for pandoc please check pandoc installation and see *.log files.")
            print("Exiting.")
            exit(0)

    def generate_pandoc_options(self):
        self.logger.info(f"Pandoc configured for export format - '{self.conversion_options[self.output_file_format]}'")
        self.pandoc_options = ['pandoc', '-f', 'html', '-t', self.conversion_options[self.output_file_format]]

        if self.pandoc_older_than_v_1_16():
            self.pandoc_options = self.pandoc_options + ['--no-wrap']
            return

        if self.pandoc_older_than_v_1_19():
            self.pandoc_options = ['--wrap=none', '-o']
            return

        if self.pandoc_older_than_v_2_11_2():
            self.pandoc_options = ['--wrap=none', '--atx-headers']
            return

        self.pandoc_options = self.pandoc_options + ['--wrap=none', '--markdown-headings=atx']

    def convert_using_strings(self, input_data, note_title):
        try:
            out = subprocess.run(self.pandoc_options, input=input_data, capture_output=True, text=True, timeout=20)
            return out.stdout
        except subprocess.CalledProcessError:
            self.logger.error(f" unable to convert note {note_title} in method {what_method_is_this()}")
            error_handling(note_title)

        return 'Error converting data'

    def convert_using_fies(self, content, note_title):
        output_file, input_file = create_temporary_files()

        file_options = self.pandoc_options + ['-o', output_file.name, input_file.name]

        Path(input_file.name).write_text(content, 'utf-8')
        try:
            pandoc = subprocess.Popen(file_options)
            pandoc.wait(20)
            return Path(output_file.name).read_text('utf-8')

        except subprocess.CalledProcessError:
            error_handling(note_title)
            self.logger.error(f"unable to convert note {note_title} in method {what_method_is_this()}")

        return 'Error converting data'

    def pandoc_older_than_v_1_16(self):
        return distutils.version.LooseVersion(self.pandoc_version) < distutils.version.LooseVersion('1.16')

    def pandoc_older_than_v_1_19(self):
        return distutils.version.LooseVersion(self.pandoc_version) < distutils.version.LooseVersion('1.19')

    def pandoc_older_than_v_2_11_2(self):
        return distutils.version.LooseVersion(self.pandoc_version) < distutils.version.LooseVersion('2.11.2')


if __name__ == '__main__':
    pc = PandocConverter('md')
    result = pc.convert_using_strings("Hello pandoc", "test_note_title")
    print(result)
    result = pc.convert_using_fies("Goodbye pandoc", "test_note_title_2")
    print(result)
