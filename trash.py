#!/usr/bin/env python3

import os
from datetime import datetime
from pathlib import Path
from PIL import Image
import re


_TRASH_SOURCE = './pictures_Trash'
_SOURCE = './pictures_metadata'
_DESTINATION = './pictures_out_trash'
_COUNT_OFFSET = 131


def main():
    os.mkdir(_DESTINATION)
    files = os.listdir(_TRASH_SOURCE)
    files.sort()
    trash_numbers: list[int] = []
    for filename in files:
        trash_numbers.append(int(filename.split('_')[-1].removesuffix('.JPG')) - _COUNT_OFFSET)

    files = os.listdir(_SOURCE)
    files.sort()
    for filename in files:
        picture_number = int(filename.split('-')[-1].removesuffix('.jpg'))
        if picture_number in trash_numbers:
            picture_path = os.path.join(_SOURCE, filename)
            trash_path = os.path.join(_DESTINATION, filename)
            print(f'Sorting out {picture_path}')
            os.rename(picture_path, trash_path)

    

        
   
       
if __name__ == '__main__':
    main()