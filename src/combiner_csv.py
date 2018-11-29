"""
This file is intended to add all the csv entries into the main sqlite file.
"""

import database
import csv
import os

#_path_ = '/home/ubuntu/pybmp180/pyscript/data'
_path_ = 'data'


with database.DatabaseManager('data') as db:
    for file in os.listdir(_path_):
        if 'csv' in file:
            _p = os.path.join(_path_, file)
            print(_p)
            with open(_p, 'rt', encoding='utf-8') as _csv:
                dr = csv.DictReader(_csv)
                for line in dr:
                    db.add_data(line['Time(date)'], line[' degree'], line[' df'],
                                line[' pascals'], line[' hectopascals'], line[' humidity'])
                    if len(db) > 500:
                        db.commit()
            db.commit()
