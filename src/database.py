#!/usr/bin/env python3

import sqlite3
from os.path import join
from sys import argv
from time import sleep

_path_ = '/home/ubuntu/pybmp180/pyscript/data'
# _path_ = 'data'
_sqlname_ = 'data.sqlite'
_backup_ = "backup.sqlite"

_insert_cmd_ = "INSERT INTO {0}('{1}', '{2}', '{3}', '{4}', '{5}', '{6}') VALUES(?, ?, ?, ?, ?, ?)"
_inserts_ = ["TIMESTAMP", "Celsius", "Fahrenheit", "Pascals", "Hecto-Pascals", "Humidity"]

_table_name_ = "bme280_living_room"

# This try statement checks the SQLite version, you might have to add more
# code here if you use version specific code. You will then have
# to tell the user that they failed to meet your requirements.
try:
    with sqlite3.connect(join(_path_, _sqlname_)) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT SQLITE_VERSION()')
        data = cursor.fetchone()
        # print("SQLite Version: %s" % data)
        cursor.execute('CREATE TABLE IF NOT EXISTS "{}" ( '
                       '"{}" TEXT NOT NULL UNIQUE, '
                       '"{}" REAL,'
                       '"{}" REAL,'
                       '"{}" REAL,'
                       '"{}" REAL,'
                       '"{}" REAL)'.format(_table_name_, *_inserts_))
except Exception as error:
    print("Failed to load Database")
    print(error)
    print(Exception)


def progress(status, remaining, total):
    print('Copied {} of {} pages...'.format(remaining - total, total))


class DatabaseManager:
    def __init__(self, path=_path_):
        self.path = path
        self.database = None
        self.command_list = []
        self.is_alive = False

    def __enter__(self):
        self.open(database=self.path)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.database.commit()
        self.close()

    def _give_db_command(self, command, args=None):
        c = self.database.cursor()
        c.execute(command, args)

    def _insert_many(self, timeout=2):
        c = self.database.cursor()
        cmd = _insert_cmd_.format(_table_name_, *_inserts_)
        for _ in range(timeout * 10):
            try:
                c.executemany(cmd, self.command_list)
            except FileNotFoundError:
                print("Failed", error)
                sleep(timeout / 10)
                pass
            finally:
                break
        else:
            c.executemany(cmd, self.command_list)
        self.command_list = []

    def commit(self):
        self._insert_many()
        self.database.commit()

    def _rollback(self):
        self.database.rollback()

    def open(self, database=_path_):
        if not self.is_alive:
            self.path = join(database, _sqlname_)
            self.database = sqlite3.connect(database=self.path)
            self.is_alive = True
        else:
            print("Database is already active.")

    def close(self):
        if self.is_alive:
            self.commit()
            self.database.close()
            self.is_alive = False
        else:
            print("Database is not active.")

    def add_data(self, *args):
        self.command_list.append((args[0], float(args[1]), float(args[2]),
                                  float(args[3]), float(args[4]), float(args[5])))

    def get_info(self, override=False):
        c = self.database.cursor()
        try:
            c.execute("SELECT {} FROM '{}'".format(override if override else '*', _table_name_))
        except sqlite3.OperationalError:
            print('{} does not exists in database'.format(override if override else '*'))
            return False
        _data = sorted(c.fetchall())
        while _data:
            yield _data.pop()

    def BACKUP(self):
        with sqlite3.connect(join(_path_, _backup_)) as _conn:
            self.database.backup(_conn, pages=1, progress=progress)

    def __len__(self):
        return len(self.command_list)

    def __str__(self):
        return self.path


if __name__ == "__main__":
    if len(argv) > 1:
        if argv[1] == 'data':
            db = DatabaseManager()
            try:
                db.open(argv[2])
                for i in db.get_info():
                    print(i)
            except IndexError:
                db.open()
                for i in db.get_info():
                    print(i)
            db.close()
    else:
        try:
            db = DatabaseManager()
            db.open()
            status = db.is_alive
            for i in db.get_info():
                print(i)
            db.close()
            print("The database was {} created".format("successfully" if status else "was not"))
        except sqlite3.OperationalError:
            pass
