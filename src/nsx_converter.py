#!/usr/bin/env python
import sys
import inspect
from pathlib import Path
import logging
import logging.handlers as handlers
from nsxfile import NSXFile
from config_data import ConfigData
from globals import APP_NAME
from interactive_cli import StartUpCommandLineInterface
from arg_parsing import CommandLineParsing
import quick_settings
from quick_settings import ConversionSettings

log_filename = 'normal.log'
error_log_filename = 'error.log'

root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)

file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')

logHandler = handlers.RotatingFileHandler(log_filename, maxBytes=2 * 1024 * 1024, backupCount=5)
logHandler.setLevel(logging.INFO)
logHandler.setFormatter(file_formatter)

errorLogHandler = handlers.RotatingFileHandler(error_log_filename, maxBytes=2 * 1024 * 1024, backupCount=5)
errorLogHandler.setLevel(logging.ERROR)
errorLogHandler.setFormatter(file_formatter)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.CRITICAL)

root_logger.addHandler(logHandler)
root_logger.addHandler(errorLogHandler)
root_logger.addHandler(console_handler)


class ConfigException(Exception):
    pass


def what_method_is_this():
    return inspect.currentframe().f_back.f_code.co_name


def what_module_is_this():
    return __name__


def main():
    main_logger = logging.getLogger(f'{APP_NAME}.{what_module_is_this()}')
    main_logger.info(f'{what_method_is_this()} - Program startup')

    command_line = CommandLineParsing()

    conversion_settings = evaluate_command_line_arguments(command_line)

    nsx_backups = fetch_nsx_backups(conversion_settings)

    process_nsx_files(nsx_backups)
    if not conversion_settings.silent:
        print("Hello. I'm done")
    main_logger.info("Processing Completed - exiting normally")


def run_interactive_command_line_interface(command_line) -> ConversionSettings:
    config_data = ConfigData('config.ini', 'gfm', allow_no_value=True)
    command_line_interface = StartUpCommandLineInterface(command_line.conversion_setting)
    conversion_settings = command_line_interface.run_cli()
    config_data.conversion_settings(conversion_settings)
    root_logger.info("Using conversion settings form interactive command line tool")
    return conversion_settings


def fetch_nsx_backups(conversion_settings) -> list[NSXFile]:
    nsx_files_to_convert = generate_file_list_to_convert(conversion_settings.source)

    if not nsx_files_to_convert:
        root_logger.info(f"No .nsx files found at path {conversion_settings.source}. Exiting program")
        if not conversion_settings.silent:
            print(f'No .nsx files found at {conversion_settings.source}')
        sys.exit(1)

    nsx_backups = [NSXFile(file, conversion_settings) for file in nsx_files_to_convert]
    return nsx_backups


def process_nsx_files(nsx_backups):
    for nsx_file in nsx_backups:
        nsx_file.process_nsx_file()


def generate_file_list_to_convert(source):
    if source.is_file():
        return source
    return source.glob('*.nsx')


def evaluate_command_line_arguments(command_line: CommandLineParsing) -> ConversionSettings:

    if command_line.args['gui']:
        root_logger.info("Using gui if it was coded....")
        if not command_line.args['silent']:
            print("gui")  # run gui
        return

    if command_line.args['ini']:
        # every time I look at his I wonder if values somebody enters after -i on the command line should be used...
        # No they should not.  they have chosen to use ini file and all the settings they need should be in it as
        # they have chosen to use the ini file

        root_logger.info("Using settings from config  ini file")
        config_data = ConfigData('config.ini', 'gfm', allow_no_value=True)
        return config_data.conversion_settings

    if command_line.args['manual']:
        return command_line.conversion_setting

    if not (command_line.args['quickset'] is None):
        # for a quick setting the source, export folder and attachment folder provided on the command line will be used
        # or the defaults if they were not provided as arguments
        root_logger.info(f"Using quick settings for {command_line.args['quickset']}")
        conversion_settings = quick_settings.please.provide(command_line.args['quickset'])
        conversion_settings.source = command_line.args['source']
        conversion_settings.export_folder_name = command_line.args['export_folder']
        conversion_settings.attachment_folder_name = command_line.args['attachments']
        return conversion_settings

    if command_line.args['silent']:
        root_logger.warning(f"Command line option -s  --silent used without -m, -g, q, or -i.  "
                            f"Unable to use Interactive command line due to silence request.  "
                            f"Exiting program")
        sys.exit(0)

    root_logger.info("Starting interactive command line tool")
    return run_interactive_command_line_interface(command_line)



if __name__ == '__main__':
    main()
