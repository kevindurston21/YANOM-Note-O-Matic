#!/usr/bin/env python

import sys
from pathlib import Path
import logging
from os.path import dirname, join
from nsxfile import NSXFile
from config_data import ConfigData


def main():

    start_logging()

    config_data = ConfigData()
    nsx_backups = fetch_nsx_backups(config_data)

    for nsx_file in nsx_backups:
        nsx_file.process_nsx_file()

    print("Hello. I'm done")


def start_logging():
    log_file = join(dirname(__file__), 'nsx_converter.log')
    logging.basicConfig(level=logging.DEBUG, filename=log_file,
                        format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')


def fetch_nsx_backups(config_data):
    nsx_files_to_convert = read_file_list_to_convert(Path.cwd)
    
    if not nsx_files_to_convert:
        print('No .nsx files found')
        exit(1)
    
    nsx_backups = [NSXFile(file, config_data) for file in nsx_files_to_convert]
    return nsx_backups

#
# def fetch_notebooks(nsx_backups):
#     return [Notebook(nsx_backup) for nsx_backup in nsx_backups]
#
#
# def fetch_pages(nsx_backups):
#     return [NotePage(nsx_backup) for nsx_backup in nsx_backups]


def read_file_list_to_convert(work_path):
    if len(sys.argv) > 1:
        return [Path(path) for path in sys.argv[1:]]
    else:
        return Path(work_path).glob('*.nsx')


if __name__ == '__main__':
    main()