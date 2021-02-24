import zipfile
import json
import sn_attachment # import Attachment, ImageAttachment, FileAttachment
from sn_attachment_writer import AttachmentWriter
from sn_zipfile_reader import NSXZipFileReader
from helper_functions import generate_clean_path


class NotePage:
    def __init__(self, nsx_file, note_id, ):
        self.zipfile_reader = nsx_file.get_zipfile_reader()
        self.config_data = nsx_file.get_config_data()
        self.note_id = note_id
        self.note_json = ''
        self.read_note_json()
        self.title = self.note_json['title']
        self.creation_time = self.note_json['ctime']
        self.modified_time = self.note_json['mtime']
        self.raw_content = self.note_json['content']
        self.parent_notebook = self.note_json['parent_id']
        self.attachments_json = self.note_json['attachment']
        self.attachments = {}
        self.converted_content = ''
        self.notebook_folder_name = ''

    def process_note(self):
        self.create_attachments()
        self.process_attachments()

    def read_note_json(self):
        self.note_json = self.zipfile_reader.read_json_data(self.note_id)

    def get_parent_notebook_id(self):
        return self.parent_notebook

    def create_attachments(self):
        for attachment_id in self.attachments_json:
            if self.attachments_json[attachment_id]['type'].startswith('image'):
                self.attachments[attachment_id] = sn_attachment.ImageAttachment(self.attachments_json[attachment_id],
                                                                                attachment_id,
                                                                                self.notebook_folder_name,
                                                                                self.config_data, self.zipfile_reader)
            else:
                self.attachments[attachment_id] = sn_attachment.FileAttachment(self.attachments_json[attachment_id],
                                                                               attachment_id,
                                                                               self.notebook_folder_name,
                                                                               self.config_data, self.zipfile_reader)

    def process_attachments(self):
        for attachment_id in self.attachments:
            self.attachments[attachment_id].process_attachment()

    def set_notebook_folder_name(self, title):
        self.notebook_folder_name = generate_clean_path(title)
