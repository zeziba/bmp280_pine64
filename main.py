import sys
import os
from datetime import datetime
from os.path import join

from Adafruit_BME280 import *


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


def main():
    timers = {
        "bme280": Timer(1),
    }

    _file_name = "data"
    header = "degree, df, pascals, hectopascals, humidity\n"
    _out = "{},{},{},{},{}\n"

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
    except OSError as oserr:
        sys.exit(-1)
    except RuntimeError as runerr:
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

    try:
        _file = join(os.path.split(os.path.abspath(os.path.realpath(sys.argv[0])))[0],
                     "data", "{}_{}.csv".format(_file_name, datetime.now().strftime("%Y-%m-%d_%H_%M_%S")))
        with open(_file, "w+") as file:
            file.write(header)
            while True:
                if timers["bme280"].check > timers["bme280"].tdelta:
                    timers["bme280"].start()
                    file.write(_out.format(*gather_data()))
                    file.flush()
    except FileNotFoundError as err:
        print(err)

