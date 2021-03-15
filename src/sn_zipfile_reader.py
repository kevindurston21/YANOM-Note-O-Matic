import zipfile
import json


class NSXZipFileReader:
    def __init__(self, nsx_file_name):
        self.zipfile_name = nsx_file_name

    def read_json_data(self, file_name):
        with zipfile.ZipFile(str(self.zipfile_name), 'r') as zip_file:
            return json.loads(zip_file.read(file_name).decode('utf-8'))

    def read_attachment_file(self, file_name):
        with zipfile.ZipFile(str(self.zipfile_name), 'r') as zip_file:
            return zip_file.read(file_name)