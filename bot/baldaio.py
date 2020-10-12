# Import standard python modules
from os import environ as secrets
from typing import Union

from Adafruit_IO import Client
from Adafruit_IO.errors import RequestError as RequestError
from twitchbot import cfg

# from main import AddOhmsBot
# Import Adafruit IO REST client.
# to get stored credientials


class AIO:
    """AdafruitIO Class"""

    def __init__(self):
        # Secret can be set in either an environment variable (used first) or config.json
        self.ADAFRUIT_IO_USERNAME = secrets.get("ADAFRUIT_IO_USERNAME", False) or cfg.adafruit_io_user
        self.ADAFRUIT_IO_KEY = secrets.get("ADAFRUIT_IO_KEY", False) or cfg.adafruit_io_key

        # The connection handle for making calls
        self.__client = None

        # Default to not connected
        self.AIO_CONNECTION_STATE = False
        self.ATTN_ENABLE = True

    def connect_to_aio(self):
        """Connect to Adafruit.IO"""
        # Create an instance of the REST client.
        if self.ADAFRUIT_IO_USERNAME is None or self.ADAFRUIT_IO_KEY is None:
            print("Adafruit IO keys not found, aborting connection")
            return False

        try:
            print("Atempting to connect to AIO as " + self.ADAFRUIT_IO_USERNAME)
            self.__client = Client(self.ADAFRUIT_IO_USERNAME, self.ADAFRUIT_IO_KEY)
            print("Connected to Adafruit.IO")
            self.AIO_CONNECTION_STATE = True
            return True

        except Exception as e:
            print("Failed to connect to AIO, disabling it")
            print(e)
            self.AIO_CONNECTION_STATE = False
            return False

    def send(self, feed, value: Union[str, int] = 1):
        """Send to an AdafruitIO topic"""
        if self.AIO_CONNECTION_STATE is False:
            try:
                if not self.connect_to_aio():
                    return False
            except Exception as e:
                print(e)
                return False

        try:
            self.__client.send_data(feed, value)
            return True
        except RequestError as e:
            print(e)
            return False
