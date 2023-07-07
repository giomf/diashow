#!/usr/bin/env python3

import os
import datetime

_SOURCE = './fotobox'
_DESTINATION = './pictures_renamed'
_DELTA = 16323432
_COUNT_OFFSET = 131

def main():

    os.mkdir(_DESTINATION)
    for filename in os.listdir(_SOURCE):
        filepath = os.path.join(_SOURCE, filename)
        if os.path.isfile(filepath):
            name_components = filename.split('_')
            year = int(name_components[0])
            month = int(name_components[1]) 
            day = int(name_components[2]) 
            hour = int(name_components[3])
            minute = int(name_components[4])
            second = int(name_components[5])
            count = int(name_components[6].removesuffix('.JPG')) - _COUNT_OFFSET

            old_date = datetime.datetime(year, month, day, hour, minute, second)
            delta = datetime.timedelta(seconds=_DELTA)
            new_date = old_date + delta

            new_filename = f'{new_date.isoformat()}-{count}.jpg'
            new_filepath = os.path.join(_DESTINATION, new_filename)
            os.rename(filepath, new_filepath)
            print(f"Renamed {filename} to {new_filepath}")

if __name__ == '__main__':
    main()