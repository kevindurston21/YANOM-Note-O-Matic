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

    config_data = ConfigData('config.ini', 'gfm', allow_no_value=True)
    config_ini_conversion_settings = config_data.get_conversion_settings()

    # TODO if some command line option then run cli, need to integrate command line parameters here
    command_line_interface = StartUpCommandLineInterface(config_ini_conversion_settings)
    conversion_settings = command_line_interface.run_cli()
    config_data.load_config_from_conversion_settings_obj(conversion_settings)

    # TODO if some command line option load config  from file only skip the CLI
    # config_data = ConfigData('config.ini', 'gfm', allow_no_value=True)

    nsx_backups = fetch_nsx_backups(conversion_settings)

    process_nsx_files(nsx_backups)

    print("Hello. I'm done")
    main_logger.info("Processing Completed - exiting normally")


def run_interactive_command_line_interface():
    cli = StartUpCommandLineInterface()
    return cli.run_cli()


def fetch_nsx_backups(conversion_settings):
    nsx_files_to_convert = read_file_list_to_convert(Path.cwd)
    
    if not nsx_files_to_convert:
        root_logger.info(f"No .nsx files found at path {nsx_files_to_convert}")
        print('No .nsx files found')
        exit(1)
    
    nsx_backups = [NSXFile(file, conversion_settings) for file in nsx_files_to_convert]
    return nsx_backups


def process_nsx_files(nsx_backups):
    for nsx_file in nsx_backups:
        nsx_file.process_nsx_file()


def read_file_list_to_convert(work_path):
    if len(sys.argv) > 1:
        return [Path(path) for path in sys.argv[1:]]
    else:
        return Path(work_path).glob('*.nsx')


if __name__ == '__main__':
    main()