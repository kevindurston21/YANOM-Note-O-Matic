import re
from abc import ABC, abstractmethod
from sn_attachment import ImageAttachment


class PreProcessing(ABC):
    """Abstract class representing a pre conversion note formatting """

    @abstractmethod
    def pre_process_note_page(self):
        pass


class CheckListItem:
    def __init__(self, raw_item_htm):
        self._raw_item_html = raw_item_htm
        self._processed_item_html = str
        self._item_checked = ' '   # note a space ' ' is unchecked and 'x' is checked
        self._item_text = str
        self._check_list_level = 1
        self.find_item_text()
        self.find_status()
        self.find_item_level()
        self.build_processed_item_html()

    @property
    def raw_item_html(self):
        return self._raw_item_html

    @property
    def processed_item_html(self):
        return self._processed_item_html

    def build_processed_item_html(self):
        tabs = '\t' * self._check_list_level
        self._processed_item_html = f"<p>-{tabs}[{self._item_checked}] {self._item_text}</p>"

    def find_item_text(self):
        matches = re.findall('<input class=[^>]*syno-notestation-editor-checkbox[^>]*src=[^>]*type=[^>]*>([^<]*)', self._raw_item_html)
        self._item_text = matches[0]

    def find_status(self):
        matches = re.findall('syno-notestation-editor-checkbox-checked', self._raw_item_html)
        if matches:
            self._item_checked = 'x'

    def find_item_level(self):
        matches = re.findall('[0-9]{2}', self._raw_item_html)
        if matches:
            indent = int(matches[0])
            self._check_list_level = indent // 30 + 1


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


class NoteStationPreProcessing(PreProcessing):
    def __init__(self, raw_content: str, attachments: dict):
        self._pre_processed_content = raw_content
        self._attachments = attachments
        self._image_attachments = []
        self._image_tags = {}
        self._image_tag_processors = []
        self._image_ref_to_image_path = {}
        self._check_list_items = []
        self.pre_process_note_page()
        pass

    @property
    def pre_processed_content(self):
        return self._pre_processed_content

    @pre_processed_content.setter
    def pre_processed_content(self, raw_content):
        self._pre_processed_content = raw_content

    def pre_process_note_page(self):
        self.create_image_tag_processors()
        self.update_content_with_new_img_tags()
        self.clean_excessive_divs()
        self.fix_ordered_list()
        self.fix_unordered_list()
        self.replace_check_lists()
        pass
        # self._pre_processed_content = '<ul><input type="checkbox" name="vehicle1" value="Bike"><label for="vehicle1"> I have a bike</label><br><input type="checkbox" name="vehicle2" value="Car"><label for="vehicle2"> I have a car</label><br><input type="checkbox" name="vehicle3" value="Boat" checked><label for="vehicle3"> I have a boat</label><br></ul>'

    def create_image_tag_processors(self):
        raw_image_tags = re.findall('<img class=[^>]*syno-notestation-image-object[^>]*src=[^>]*ref=[^>]*>',
                                    self._pre_processed_content)
        self._image_tag_processors = [ImageTag(tag, self._attachments) for tag in raw_image_tags]

    def update_content_with_new_img_tags(self):
        for image_tag_processor in self._image_tag_processors:
            self._pre_processed_content = self._pre_processed_content.replace(image_tag_processor.raw_tag,
                                                                              image_tag_processor.processed_tag)

    def clean_excessive_divs(self):
        """
        Replace all the div's with p's
        """
        self._pre_processed_content = self._pre_processed_content.replace('<div></div>', '<p></p>')
        self._pre_processed_content = self._pre_processed_content.replace('<div', '<p')
        self._pre_processed_content = self._pre_processed_content.replace('</div', '</p')

    def fix_ordered_list(self):
        self._pre_processed_content = self._pre_processed_content.replace('</li><ol>', '<ol>')
        self._pre_processed_content = self._pre_processed_content.replace('</li></ol>', '</li></li></ol>')

    def fix_unordered_list(self):
        self._pre_processed_content = self._pre_processed_content.replace('</li><ul>', '<ul>')
        self._pre_processed_content = self._pre_processed_content.replace('</li></ul>', '</li></li></ul>')

    def replace_check_lists(self):
        pass

        raw_checklists_item = re.findall(
            '<p[^>]*><input class=[^>]*syno-notestation-editor-checkbox[^>]*src=[^>]*type=[^>]*>[^<]*</p>',
            self._pre_processed_content)

        check_list_items = [CheckListItem(item) for item in raw_checklists_item]
        self._check_list_items = {id(item): item for item in check_list_items}
        pass

        for item in self._check_list_items.values():
            # Using 'check-list-id(item)' as a checklist item place holder as pandoc cannot cleanly convert checklists,
            # the unique id will be used to replace the id with good checklist items in post processing.
            self._pre_processed_content = self._pre_processed_content.replace(item.raw_item_html,
                                                                              f'<p>check-list-{str(id(item))}</p>')

        # TODO in post processing the note page has the pre processing object use this
        # and inside that we can get the checklist items from the _check_list_items dict
        # where id is the key and the value is the checklist item which has the processed
        # item text to replace the id with
