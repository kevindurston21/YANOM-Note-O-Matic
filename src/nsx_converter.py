#!/usr/bin/env python

import sys
from pathlib import Path
import logging
from os.path import dirname, join
from nsxfile import NSXFile
from sn_config_data import ConfigData
from config_data import ConfigData


class ConfigException(Exception):
    pass


def main():

    start_logging()

    logging.info("Creating instance of sn_config_data.ConfigData")
    config_data = ConfigData('config.ini', 'gfm', allow_no_value=True)

    config_data.load_quick_setting('obsidian')

    nsx_backups = fetch_nsx_backups(config_data)

    for nsx_file in nsx_backups:
        nsx_file.process_nsx_file()

    print("Hello. I'm done")


def start_logging():

    # create logger with 'yanom-application'
    logger = logging.getLogger('yanom-application')
    logger.setLevel(logging.DEBUG)
    # create file handler which logs even debug messages
    fh = logging.FileHandler('yanom-application.log')
    fh.setLevel(logging.DEBUG)
    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.ERROR)
    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    # add the handlers to the logger
    logger.addHandler(fh)
    logger.addHandler(ch)
    logger.info("program startup - logging enabled")


def fetch_nsx_backups(config_data):
    nsx_files_to_convert = read_file_list_to_convert(Path.cwd)
    
    if not nsx_files_to_convert:
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