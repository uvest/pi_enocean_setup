# A class for the nodon temperature and humidity sensor
# It does a very rudimentary translation of the data
# The translation is based on own measurements and the list provided by kipe at
#   https://github.com/kipe/enocean/blob/master/SUPPORTED_PROFILES.md
#   RORG 0xA5 - FUNC 0x04 - TYPE 0x01 - Range 0°C to +40°C and 0% to 100%
#   0.0-250.0 (translates to) 0.0-100.0 %
#   0.0-250.0 (translates to) 0.0-40.0 °C

from typing import Tuple


class Nodon():
    def __init__(self) -> None:
        self.temp_raw_min = 0
        self.temp_raw_max = 250
        self.humid_raw_min = 0
        self.humid_raw_max = 250

        self.temp_min = 0 # °C
        self.temp_max = 40 # °C
        self.temp_range = self.temp_max - self.temp_min

        self.humid_min = 0
        self.humid_max = 1
        self.humid_range = self.humid_max - self.humid_min

    def translate(self, raw:list) -> Tuple:
        """
            parameters:
                - raw: list - the raw data received from the nod-on sensor.
                    e.g. : [165, 0, 145, 54, 10, 5, 151, 44, 173, 0]
            return:
                - temperature: float - in °C
                - humidity: float - humidity ranging from 0 to 1
        """
        # make sure the data was really from a sensor of type BS4
        if (raw[0] != 165 or len(raw) != 10):
            return "unknown", None
        elif raw[1] == 16:
            return "learning message", None
        else:
            temperature = self.temp_min +  ( (raw[3] - self.temp_raw_min) / self.temp_raw_max ) * self.temp_range
            # for humidity this simplifies to: humidity = raw[2] / self.humid_raw_max
            humidity = self.humid_min + ( (raw[2] - self.humid_raw_min) / self.humid_raw_max ) * self.humid_max

            return "temp_and_hum", (temperature, humidity)
