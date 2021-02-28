import object_factory
from abc import ABC, abstractmethod


class QuickSettingProvider(object_factory.ObjectFactory):
    def provide(self, quick_setting, **_ignored):
        return self.create(quick_setting)


class QuickSettings(ABC):
    def __init__(self, **kwargs):
        self.output_file_types = ['md', 'pdf']
        self.valid_export_formats = ['manual', 'q_own_notes', 'obsidian', 'gfm', 'pdf']
        # self.current_quick_set = ''  # this may not be needed currently set and never used.. probably a good idea at the time...

        self.quick_settings = {f'    # Valid entries are {", ".join(self.valid_export_formats)[:-2]}': None,
                               '    # use manual to use manual settings below': None,
                               '    # NOTE is an option other than - manual - is used the rest of the '
                               '    # settings in this file will be set automatically'
                               '    #': None,
                               "quick_setting": 'gfm',
                               '    # ': None,
                               '    # The following sections only apply if all of the above are no': None,
                               '    #': None}

        self.export_formats = {f'    # Valid entries are {", ".join(self.valid_export_formats)[:-2]}': None,
                               "export_format": "gfm"}

        # if you change this changes are likely in all places that call this method
        self.meta_data_options = {'include_meta_data': 'yes',
                                  '    # Note if include_meta_data = no then the following values will': None,
                                  '    # not be included in the export file': None,
                                  'yaml_meta_header_format': 'no', 'insert_title': 'yes',
                                  'insert_creation_time': 'yes', 'insert_modified_time': 'yes',
                                  'include_tags': 'yes', 'tag_prefix': '#',
                                  'no_spaces_in_tags': 'yes', 'split_tags': 'no'}

        # if you change this changes are likely in all places that call this method
        self.file_options = {'export_folder_name': 'notes',
                             'attachment_folder_name': 'attachments',
                             'creation_time_in_exported_file_name': 'no'}

        # if you change this changes are likely in all places that call this method
        self.image_link_formats = {'    # valid entries are': None,
                                   '    # strict_md     which looks like [](path to image)': None,
                                   '    # gfm-html      which looks like <img src=path to file width=width_value>': None,
                                   '    # obsidian      which looks like [|width_value](path to image)': None,
                                   'image_link_format': 'strict_md'}

        self.set_quick_settings()

    @abstractmethod
    def set_quick_settings(self):
        pass

    def provide_quick_settings(self):
        return {'quick_settings': self.quick_settings, 'export_formats': self.export_formats,
                'meta_data_options': self.meta_data_options, 'file_options': self.file_options,
                'image_link_formats': self.image_link_formats}


class ManualQuickSettings(QuickSettings):
    def set_quick_settings(self):
        pass


class QOwnNotesQuickSettings(QuickSettings):
    def __init__(self):
        super().__init__()

    def set_quick_settings(self):
        self.export_formats = 'q_own_notes'
        self.image_link_formats['image_link_format'] = 'strict_md'


class GfmQuickSettings(QuickSettings):
    def set_quick_settings(self):
        self.meta_data_options['yaml_meta_header_format'] = 'yes'
        self.image_link_formats['image_link_format'] = 'gfm-html'


class ObsidianQuickSettings(QuickSettings):
    def set_quick_settings(self):
        self.meta_data_options['yaml_meta_header_format'] = 'yes'
        self.image_link_formats['image_link_format'] = 'obsidian'


class PdfQuickSettings(QuickSettings):
    def set_quick_settings(self):
        self.meta_data_options['include_meta_data'] = 'no'


please = QuickSettingProvider()
please.register_builder('manual', ManualQuickSettings)
please.register_builder('q_own_notes', QOwnNotesQuickSettings)
please.register_builder('gfm', GfmQuickSettings)
please.register_builder('obsidian', ObsidianQuickSettings)
please.register_builder('pdf', PdfQuickSettings)

