#!/usr/bin/env python
import sys
import inspect
from pathlib import Path
import logging
import logging.handlers as handlers
from nsxfile import NSXFile
from config_data import ConfigData
from globals import APP_NAME


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

    nsx_backups = fetch_nsx_backups(config_data)

    for nsx_file in nsx_backups:
        nsx_file.process_nsx_file()

    print("Hello. I'm done")
    main_logger.info("Processing Completed - exiting normally")


def fetch_nsx_backups(config_data):
    nsx_files_to_convert = read_file_list_to_convert(Path.cwd)
    
    if not nsx_files_to_convert:
        root_logger.info(f"No .nsx files found at path {nsx_files_to_convert}")
        print('No .nsx files found')
        exit(1)
    
    nsx_backups = [NSXFile(file, config_data) for file in nsx_files_to_convert]
    return nsx_backups


def read_file_list_to_convert(work_path):
    if len(sys.argv) > 1:
        return [Path(path) for path in sys.argv[1:]]
    else:
        return Path(work_path).glob('*.nsx')


if __name__ == '__main__':
    main()