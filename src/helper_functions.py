import urllib.request
from urllib.parse import unquote
import unicodedata
import re
from pathlib import Path


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


