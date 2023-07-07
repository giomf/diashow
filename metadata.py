#!/usr/bin/env python3

import os
from datetime import datetime
from pathlib import Path
from PIL import Image
import re


_SOURCE = './pictures_renamed'
_DESTINATION = './pictures_metadata'


def main():
    os.mkdir(_DESTINATION)
    files = os.listdir(_SOURCE)
    files.sort()
    for filename in files:
        date = get_date_from_file(filename)
        overwrite_metadata(filename, date)
    

def get_date_from_file(filename: str) -> datetime:
    pattern = r"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})"
    match = re.search(pattern, filename)
    if match is None:
        raise ValueError
    return datetime.strptime(match.group(1), "%Y-%m-%dT%H:%M:%S")
   
def overwrite_metadata(filename: str, date: datetime):
    original = Path(_SOURCE).joinpath(filename)
    destination = Path(_DESTINATION).joinpath(filename)


    try:
        image = Image.open(original)
        exif_data = image.getexif()
        if exif_data is None:
            raise RuntimeError
        exif_data.get_ifd(34665)[36867] = date.strftime("%Y:%m:%d %H:%M:%S")
        exif_data.get_ifd(34665)[306] = date.strftime("%Y:%m:%d %H:%M:%S")
        exif_data.get_ifd(36868)[306] = date.strftime("%Y:%m:%d %H:%M:%S")
        image.save(destination, exif=exif_data, quality=97)
        print(f"Metadata overwritten for {filename}")
    except Exception as e:
        print(f"Failed to overwrite metadata for {filename}: {e}")

   
if __name__ == '__main__':
    main()