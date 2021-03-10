import re
from abc import ABC, abstractmethod
from sn_attachment import ImageAttachment


class PreProcesing(ABC):
    """Abstract class representing a pre conversion note formatting """

    @abstractmethod
    def pre_process_note_page(self):
        pass


class ImageTag:
    def __init__(self, raw_tag, attachments):
        self._attachments = attachments
        self._raw_tag = raw_tag
        self._processed_tag = ''
        self._ref = ''
        self._width = ''
        self._relative_path = ''
        self.__set_ref_and_relative_path()
        self.__set_width()
        self._processed_tag = f"<img src={self._relative_path} {self._width}>"
        pass

    def __set_ref_and_relative_path(self):
        for attachment in self._attachments.values():
            if isinstance(attachment, ImageAttachment) and attachment.image_ref in self._raw_tag:
                self._ref = attachment.image_ref
                self._relative_path = str(attachment.path_relative_to_notebook)

    def __set_width(self):
        if 'width="' in self._raw_tag:
            width = re.findall('width="[0-9]*"', self._raw_tag)
            self._width = width[0]

    @property
    def processed_tag(self):
        return self._processed_tag

    @property
    def raw_tag(self):
        return self._raw_tag


class NoteStationPreProcessing(PreProcesing):
    def __init__(self, raw_content: str, attachments: dict):
        self._pre_processed_content = raw_content
        self._attachments = attachments
        self._image_attachments = []
        self._image_tags = {}
        self._image_tag_processors= []
        self._image_ref_to_image_path = {}
        self.pre_process_note_page()

    @property
    def pre_processed_content(self):
        return self._pre_processed_content

    @pre_processed_content.setter
    def pre_processed_content(self, raw_content):
        self._pre_processed_content = raw_content

    def pre_process_note_page(self):
        self.create_image_tag_processors()
        self.update_content_with_new_img_tags()
        pass

    def create_image_tag_processors(self):
        raw_image_tags = re.findall('<img class=[^>]*syno-notestation-image-object[^>]*src=[^>]*ref=[^>]*>',
                                    self._pre_processed_content)
        self._image_tag_processors = [ImageTag(tag, self._attachments) for tag in raw_image_tags]


    def update_content_with_new_img_tags(self):
        for image_tag_processor in self._image_tag_processors:
            self._pre_processed_content = self._pre_processed_content.replace(image_tag_processor.raw_tag,
                                                                              image_tag_processor.processed_tag)

    # def clean_excessive_divs(self):
    #     """
    #     Remove all the div's not containing only line breaks
    #     """
    #     self._pre_processed_content = re.sub('<div></div>', '', self._pre_processed_content)
    #
    #     # below was done in post processing
    #     # self.page_content = re.sub('\n<div>\n', '', self.page_content)
    #     # self.page_content = re.sub('\n</div>\n', '', self.page_content)
