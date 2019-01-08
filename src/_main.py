#!/usr/bin/env python3

import signal
import sys
from datetime import datetime
from time import sleep
import database

from Adafruit_BME280 import *

DEBUG = False
BACKUP = False


class SignalWatch:
    kill = False

    def __init__(self):
        signal.signal(signal.SIGINT, self._exit)
        signal.signal(signal.SIGTERM, self._exit)

    def _exit(self, signum, frame):
        self.kill = True


class Timer:
    def __init__(self, interval):
        self.interval = interval
        self.time = None

    def start(self):
        self.time = datetime.now()

    def stop(self):
        self.start = None

    @property
    def check(self):
        return (datetime.now() - self.time).total_seconds()

    @property
    def tdelta(self):
        return self.interval

    def __sub__(self, other):
        return (self.time - other.time)

    def __add__(self, other):
        return (self.time + other.time)

    def __str__(self):
        if self.time is not None:
            return str((datetime.now() - self.time).total_seconds())
        else:
            return "None"


signal_watch = SignalWatch()


def main():
    timers = {
        "bme280": Timer(180),
    }

    _file_name = "data"

    # Have to override the get_default_bus for the Adafruit.GPIO.I2C
    # The Pine64 uses the secondary bus so it needs to return 1, if different change this return value
    import Adafruit_GPIO.I2C as I2C

    def get_default_bus():
        return 1

    I2C.get_default_bus = get_default_bus

    def get_sensor():
        return BME280(t_mode=BME280_OSAMPLE_8, p_mode=BME280_OSAMPLE_8, h_mode=BME280_OSAMPLE_8, address=0x76)

    try:
        sensor = get_sensor()
    except OSError:
        sys.exit(-1)
    except RuntimeError:
        sys.exit(-2)

    def gather_data():
        degrees = sensor.read_temperature()
        df = sensor.read_temperature_f()
        pascals = sensor.read_pressure()
        hectopascals = pascals / 100
        humidity = sensor.read_humidity()
        return degrees, df, pascals, hectopascals, humidity

    out = {
        "tempc": 'Temp      = {0:0.3f} deg C',
        "tempf": 'Temp      = {0:0.3f} deg F',
        "pressure": 'Pressure  = {0:0.2f} hPa',
        "humidity": 'Humidity  = {0:0.2f} %'
    }

    for timer in timers.values():
        timer.start()

    _wait = True
    try:
        global signal_watch
        global BACKUP

        with database.DatabaseManager() as _db:
            while not signal_watch.kill:
                if timers["bme280"].check > timers["bme280"].tdelta:
                    if DEBUG:
                        data = gather_data()
                        print(data)
                        print(out['tempc'].format(data[0]))
                        print(out['tempf'].format(data[1]))
                        print(out['pressure'].format(data[2]))
                        print(out['humidity'].format(data[4]))
                    else:
                        _db.add_data(timers["bme280"].time.strftime("%Y-%m-%d %H:%M:%S"), *gather_data())
                        _db.commit()

                    timers["bme280"].start()

                if _wait:
                    sleep(1)
                    _db.backup = BACKUP

                if _db.backup:
                    _db.BACKUP()
    except FileNotFoundError as err:
        print(err)


if __name__ == "__main__":
    with database.DatabaseManager() as db:
        dt = "2018-11-24 07:48:54"
        c = '22.755369503429392'
        f = '72.9596651061729'
        p = '84456.90144499036'
        hp = '844.5690144499036'
        h = '21.803302389095357'

        db.add_data(dt, c, f, p, hp, h)
        print(db)


