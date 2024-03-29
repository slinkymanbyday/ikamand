"""
Python wrapper package for the Ikamand.

This code is released under the terms of the MIT license. See the LICENSE
file for more details.
"""
import logging
import time
from urllib.parse import parse_qs
import requests
from ikamand.const import (
    GOOD_HTTP_CODES,
    COOK_START,
    TARGET_PIT_TEMP,
    TARGET_FOOD_TEMP,
    FOOD_PROBE,
    CURRENT_TIME,
    COOK_END_TIME,
    COOK_ID,
    PROBE_PIT,
    PROBE_1,
    PROBE_2,
    PROBE_3,
    GRILL_END_TIME,
    GRILL_START,
    FALSE_TEMPS,
    FAN_SPEED,
    UNKOWN_VAR,
    WIFI_SSID,
    WIFI_PASS,
    WIFI_USER
)

_LOGGER = logging.getLogger(__name__)
HTTP_ERRORS = (
    requests.exceptions.ConnectionError,
    requests.exceptions.HTTPError,
)
TIMEOUT = 5


class Ikamand:
    """A class for the iKamand API."""

    def __init__(self, ip):
        """Initialize the class."""
        self._session = requests.session()
        self.base_url = f"http://{ip}/cgi-bin/"
        self._data = {}
        self._network = {}
        self._online = False
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "ikamand",
        }
        
    def set_network(self,
                    ssid: str,
                    username: str,
                    password: str):
        """Set SSID details, untested by author"""
        
        url = f"{self.base_url}netset"
        data = {
            WIFI_SSID: ssid,
            WIFI_USER: username,
            WIFI_PASS: password
        }
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "ikamand"
        }
        try:
            self._session.post(
                url, headers=headers, data=data, timeout=TIMEOUT
            )
            _LOGGER.info("Network set, you will now need to connect to the same network and use the new iKamand IP address.")
        except HTTP_ERRORS as error:
            _LOGGER.error("Error connecting to iKamand, %s", error)
            
    def get_network(self):
        """Return network details"""
        
        url = f"{self.base_url}wifi_list"
        try:
            response = self._session.get(
                url, headers=self.headers, timeout=TIMEOUT
            )
            print(response)
            result = parse_qs(response.text)
            if response.status_code in GOOD_HTTP_CODES:
                self._network = result
            else:
                _LOGGER.error("Error, unable to get iKamand network data ")
        except HTTP_ERRORS as error:
            _LOGGER.error("Error connecting to iKamand, %s", error)

        return self._network


    def get_data(self):
        """Get grill information."""
        self._data = {}

        url = f"{self.base_url}data"
        try:
            response = self._session.get(
                url, headers=self.headers, timeout=TIMEOUT
            )
            result = parse_qs(response.text)
            if response.status_code in GOOD_HTTP_CODES:
                self._data = result
                self._online = True
            else:
                _LOGGER.error("Error, unable to get iKamand data ")
        except HTTP_ERRORS:
            self._online = False
        return self._data

    def start_cook(
        self,
        target_pit_temp: int,
        target_food_temp: int = 0,
        food_probe: int = 0,
    ):
        """Start iKamand Cook."""
        url = f"{self.base_url}cook"
        current_time = int(time.time())
        data = {
            COOK_START: 1,
            COOK_ID: "",
            TARGET_PIT_TEMP: target_pit_temp,
            COOK_END_TIME: current_time + 86400,
            FOOD_PROBE: food_probe,
            TARGET_FOOD_TEMP: target_food_temp,
            UNKOWN_VAR: 0,
            CURRENT_TIME: current_time,
        }
        try:
            self._session.post(
                url, headers=self.headers, data=data, timeout=TIMEOUT
            )
            self._online = True
        except HTTP_ERRORS as error:
            _LOGGER.error("Error connecting to iKamand, %s", error)
            self._online = False

    def stop_cook(self):
        """Stop iKamand Cook."""
        url = f"{self.base_url}cook"
        current_time = int(time.time())
        data = {
            COOK_START: 0,
            COOK_ID: "",
            TARGET_PIT_TEMP: 0,
            TARGET_FOOD_TEMP: 0,
            FOOD_PROBE: 0,
            CURRENT_TIME: current_time,
            COOK_END_TIME: 0
        }
        try:
            self._session.post(
                url, headers=self.headers, data=data, timeout=TIMEOUT
            )
            self._online = True
        except HTTP_ERRORS as error:
            _LOGGER.error("Error connecting to iKamand, %s", error)
            self._online = False

    def start_grill(self):
        """Start iKamand Grill mode (10 minutes full speed)."""
        url = f"{self.base_url}cook"
        current_time = int(time.time())
        data = {
            GRILL_START: 1,
            GRILL_END_TIME: current_time + 10 * 60,
            CURRENT_TIME: current_time,
        }
        try:
            self._session.post(
                url, headers=self.headers, data=data, timeout=TIMEOUT
            )
            self._online = True
        except HTTP_ERRORS as error:
            _LOGGER.error("Error connecting to iKamand, %s", error)
            self._online = False

    def stop_grill(self):
        """Stop iKamand Grill mode."""
        url = f"{self.base_url}cook"
        current_time = int(time.time())
        data = {
            GRILL_START: 0,
            GRILL_END_TIME: 0,
            CURRENT_TIME: current_time,
        }
        try:
            self._session.post(
                url, headers=self.headers, data=data, timeout=TIMEOUT
            )
            self._online = True
        except HTTP_ERRORS as error:
            _LOGGER.error("Error connecting to iKamand, %s", error)
            self._online = False

    @property
    def data(self):
        """Return data."""
        return self._data

    @property
    def cooking(self):
        """Return cooking status."""
        return self._data.get(COOK_START, [0])[0] == "1"

    @property
    def grilling(self):
        """Return cooking status."""
        return self._data.get(GRILL_START, [0])[0] == "1"

    @property
    def pit_temp(self):
        """Return current pit temp."""
        return (
            int(self._data.get(PROBE_PIT, ["400"])[0])
            if self._data.get(PROBE_PIT, ["400"])[0] not in FALSE_TEMPS
            else None
        )

    @property
    def target_pit_temp(self):
        """Return target pit temp."""
        return int(self._data.get(TARGET_PIT_TEMP, [0])[0])

    @property
    def probe_1(self):
        """Return current probe 1 temp."""
        return (
            int(self._data.get(PROBE_1, ["400"])[0])
            if self._data.get(PROBE_1, ["400"])[0] not in FALSE_TEMPS
            else None
        )

    @property
    def probe_2(self):
        """Return current probe 2 temp."""
        return (
            int(self._data.get(PROBE_2, ["400"])[0])
            if self._data.get(PROBE_2, ["400"])[0] not in FALSE_TEMPS
            else None
        )

    @property
    def probe_3(self):
        """Return current probe 3 temp."""
        return (
            int(self._data.get(PROBE_3, ["400"])[0])
            if self._data.get(PROBE_3, ["400"])[0] not in FALSE_TEMPS
            else None
        )

    @property
    def fan_speed(self):
        """Return current fan speed %."""
        return int(self._data.get(FAN_SPEED, ["0"])[0])

    @property
    def online(self):
        """Return if reachable."""
        return self._online
