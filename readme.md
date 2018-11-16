This program gets data from the BMP180 sensor.
It uses a pine64 as its base.

In order to get this to work the following needs to be installed.

i2c-tools
python3-dev
python3-Adafruit-GPIO

RPi.GPIO also needs to be installed, if the pine64
is not working install the pine64 gpio library.
https://github.com/swkim01/RPi.GPIO-PineA64

After those are installed the included Adafruit bmp280 library
needs to be installed.

The program is able to run by overriding he Adafruit I2C library
and forcing the program to return the correct setting for the
BMP280 library to use. Once this is done the device is able
to communicate correctly.