import re
from abc import ABC, abstractmethod
from sn_attachment import ImageNSAttachment, ChartStringNSAttachment, ChartImageNSAttachment
from charts import NSChart
import logging
from globals import APP_NAME
import inspect


def what_module_is_this():
    return __name__


def what_method_is_this():
    return inspect.currentframe().f_back.f_code.co_name


def what_class_is_this(obj):
    return obj.__class__.__name__


class PreProcessing(ABC):
    """Abstract class representing a pre conversion note formatting """

    @abstractmethod
    def pre_process_note_page(self):
        pass


class CheckListItem:
    def __init__(self, raw_item_htm):
        self._raw_item_html = raw_item_htm
        self._processed_item_html = str
        self._item_checked = ' '  # note a space ' ' is unchecked and 'x' is checked
        self._item_text = str
        self._check_list_level = 1
        self.__find_item_text()
        self.__find_status()
        self.__find_item_level()
        self.__build_processed_item_html()

    @property
    def raw_item_html(self):
        return self._raw_item_html

    @property
    def processed_item_html(self):
        return self._processed_item_html

    def __build_processed_item_html(self):
        tabs = '\t' * self._check_list_level
        self._processed_item_html = f"<p>-{tabs}[{self._item_checked}] {self._item_text}</p>"

    def __find_item_text(self):
        matches = re.findall('<input class=[^>]*syno-notestation-editor-checkbox[^>]*src=[^>]*type=[^>]*>([^<]*)',
                             self._raw_item_html)
        self._item_text = matches[0]

    def __find_status(self):
        matches = re.findall('syno-notestation-editor-checkbox-checked', self._raw_item_html)
        if matches:
            self._item_checked = 'x'

    def __find_item_level(self):
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
            if isinstance(attachment, ImageNSAttachment) and attachment.image_ref in self._raw_tag:
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
    def __init__(self, note):
        self.logger = logging.getLogger(f'{APP_NAME}.{what_module_is_this()}.{what_class_is_this(self)}')
        self.logger.setLevel(logging.DEBUG)
        self._note = note
        self._pre_processed_content = note.raw_content
        self._attachments = note.attachments
        self._image_attachments = []
        self._image_tags = {}
        self._image_tag_processors = []
        self._image_ref_to_image_path = {}
        self._check_list_items = {}
        self._charts = []
        self.pre_process_note_page()
        pass

    @property
    def pre_processed_content(self):
        return self._pre_processed_content

    @pre_processed_content.setter
    def pre_processed_content(self, content):
        self._pre_processed_content = content

    def pre_process_note_page(self):
        self.logger.info(f"Pre processing of note page {self._note.title}")
        self.__create_image_tag_processors()
        self.__update_content_with_new_img_tags()
        self.__clean_excessive_divs()
        self.__fix_ordered_list()
        self.__fix_unordered_list()
        self.__replace_check_lists()
        self.__extract_and_generate_chart()
        pass

    def __create_image_tag_processors(self):
        self.logger.info(f"Cleaning image tags")
        raw_image_tags = re.findall('<img class=[^>]*syno-notestation-image-object[^>]*src=[^>]*ref=[^>]*>',
                                    self._pre_processed_content)
        self._image_tag_processors = [ImageTag(tag, self._attachments) for tag in raw_image_tags]

    def __update_content_with_new_img_tags(self):
        for image_tag_processor in self._image_tag_processors:
            self._pre_processed_content = self._pre_processed_content.replace(image_tag_processor.raw_tag,
                                                                              image_tag_processor.processed_tag)

    def __clean_excessive_divs(self):
        """
        Replace all the div's with p's
        """
        self.logger.info(f"Cleaning html <div")
        self._pre_processed_content = self._pre_processed_content.replace('<div></div>', '<p></p>')
        self._pre_processed_content = self._pre_processed_content.replace('<div', '<p')
        self._pre_processed_content = self._pre_processed_content.replace('</div', '</p')

    def __fix_ordered_list(self):
        self.logger.info(f"Cleaning number lists")
        self._pre_processed_content = self._pre_processed_content.replace('</li><ol>', '<ol>')
        self._pre_processed_content = self._pre_processed_content.replace('</li></ol>', '</li></li></ol>')

    def __fix_unordered_list(self):
        self.logger.info(f"Cleaning bullet lists")
        self._pre_processed_content = self._pre_processed_content.replace('</li><ul>', '<ul>')
        self._pre_processed_content = self._pre_processed_content.replace('</li></ul>', '</li></li></ul>')

    def __replace_check_lists(self):
        self.logger.info(f"Cleaning check lists")

        raw_checklists_items = re.findall(
            '<p[^>]*><input class=[^>]*syno-notestation-editor-checkbox[^>]*src=[^>]*type=[^>]*>[^<]*</p>',
            self._pre_processed_content)

        check_list_items = [CheckListItem(item) for item in raw_checklists_items]
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

    def __extract_and_generate_chart(self):
        self.logger.info(f"Cleaning charts")
        raw_charts_html = re.findall('<p[^>]*><p class=[^>]*syno-ns-chart-object[^>]*></p>',
                                     self._pre_processed_content)

        if raw_charts_html:
            self._charts = {NSChart(raw_chart): raw_chart for raw_chart in raw_charts_html}

            for chart, raw_chart_html in self._charts.items():
                self.__generate_csv_attachment(chart)
                self.__generate_png_attachment(chart)
                self.__replace_raw_chart_html_with_pre_processed_html(chart, raw_chart_html)

    def __generate_csv_attachment(self, chart):
        self._note.attachments[f"{id(chart)}.csv"] = ChartStringNSAttachment(self._note, f"{id(chart)}.csv",
                                                                             chart.csv_chart_data_string)
        self._note.attachment_count += 1

    def __generate_png_attachment(self, chart):
        self._note.attachments[f"{id(chart)}.png"] = ChartImageNSAttachment(self._note, f"{id(chart)}.png",
                                                                            chart.png_img_buffer)
        self._note.image_count += 1

    def __generate_replacement_html(self, chart):
        return f"<p>{self._note.attachments[f'{id(chart)}.png'].html_link}</p>" \
               f"<p>{self._note.attachments[f'{id(chart)}.csv'].html_link}</p>" \
               f"<p>{chart.html_chart_data_table}</p>"

    def __replace_raw_chart_html_with_pre_processed_html(self, chart, raw_charts_html):
        replacement_html = self.__generate_replacement_html(chart)
        self.pre_processed_content = self.pre_processed_content.replace(raw_charts_html, replacement_html)
