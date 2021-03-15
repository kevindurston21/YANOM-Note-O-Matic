import unicodedata
import re
import io
from pathlib import Path
import random
import string


def generate_clean_path(value, allow_unicode=False):
    """
    This function is adapted from https://github.com/django/django/blob/master/django/utils/text.py
    Copyright (c) Django Software Foundation and individual contributors.
    All rights reserved.
    Convert to ASCII if 'allow_unicode' is False. Convert spaces or repeated
    dashes to single dashes. Remove characters that aren't alphanumerics,
    underscores, or hyphens. Convert to lowercase. Also strip leading and
    trailing whitespace, dashes, and underscores.

    value: str of path of a path part - a folder name, or a file name
    returns: Path object
    """
    value = str(value)
    parts = [Path(value).stem, Path(value).suffix]
    for i in range(len(parts)):
        if not len(parts[i]):
            continue

        if allow_unicode:
            parts[i] = unicodedata.normalize('NFKC', parts[i])
        else:
            parts[i] = unicodedata.normalize('NFKD', parts[i]).encode('ascii', 'ignore').decode('ascii')
        parts[i] = re.sub(r'[^\w\s-]', '', parts[i].lower())

        parts[i] = re.sub(r'[-\s]+', '-', parts[i]).strip('-_')

    if len(parts[1]):
        return Path(f"{parts[0]}.{parts[1]}")

    return Path(parts[0])


def get_random_string(length):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))


def generate_new_filename(path):
    stem = Path(path).stem
    stem = f"{stem}-{get_random_string(4)}"
    new_filename = f"{stem}{Path(path).suffix}"
    path = Path(Path(path).parent, new_filename)
    return path


def bool_to_word(bool_value):
    if bool_value:
        return "yes"
    if not bool_value:
        return "no"


def fig_to_img_buf(fig):
    """Convert a Matplotlib figure to a io.Bytes buffer and return it"""
    buf = io.BytesIO()
    fig.savefig(buf, format='png')  # png is often smaller than jpeg for plots
    buf.seek(0)
    return buf


def add_strong_between_tags(front_tag, rear_tag, old_html):
    old_values = find_tags(front_tag, rear_tag, old_html)
    new_values = [f'<strong>{item}</strong>' for item in old_values]
    return update_html_with_changed_tags(front_tag, rear_tag, front_tag, rear_tag,
                                         old_html, old_values, new_values)


def change_html_tags(front_tag, rear_tag, new_front_tag, new_rear_tag, old_html):
    values = find_tags(front_tag, rear_tag, old_html)
    return update_html_with_changed_tags(front_tag, rear_tag, new_front_tag, new_rear_tag,
                                         old_html, values)


def update_html_with_changed_tags(front_tag, rear_tag, new_front_tag, new_rear_tag,
                                  html, old_values, new_values=None):
    if new_values is None:
        new_values = old_values
    for i in range(len(old_values)):
        html = html.replace(f'{front_tag}{old_values[i]}{rear_tag}',
                            f'{new_front_tag}{new_values[i]}{new_rear_tag}')
    return html


def find_tags(front_tag, rear_tag, html):
    return re.findall(f'{front_tag}([^<]*){rear_tag}', html)


class HTMLTagChanger:
    def __init__(self, html, current_front_tag, current_rear_tag, new_front_tag=None, new_rear_tag=None):
        self._html = html
        self._current_front_tag = current_front_tag
        self._current_rear_tag = current_rear_tag
        self._new_front_tag = new_front_tag
        self._new_rear_tag = new_rear_tag
        self._new_html = ''
        self._tag_contents = ''
        self._new_tag_contents = None

    def find_tag_contents(self):
        self._tag_contents = re.findall(f'{self._current_front_tag}([^<]*){self._current_rear_tag}', self._html)

    def __update_html_with_changed_tags(self):
        if self._new_tag_contents is None:
            self._new_tag_contents = self._tag_contents
        if self._new_front_tag is None:
            self._new_front_tag = self._current_front_tag
        if self._new_rear_tag is None:
            self._new_rear_tag = self._current_rear_tag

        for i in range(len(self._tag_contents)):
            self._html = self._html.replace(f'{self._current_front_tag}{self._tag_contents[i]}{self._current_rear_tag}',
                                            f'{self._new_front_tag}{self._new_tag_contents[i]}{self._new_rear_tag}')

    def change_html_tags(self):
        self.find_tag_contents()
        self.__update_html_with_changed_tags()

    def add_strong_between_tags(self):
        self.find_tag_contents()
        self._new_tag_contents = [f'<strong>{item}</strong>' for item in self._tag_contents]
        self.__update_html_with_changed_tags()


if __name__ == '__main__':
    pass
