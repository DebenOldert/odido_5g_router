"""Integration 101 Template integration using DataUpdateCoordinator."""

from dataclasses import dataclass
from datetime import timedelta
import logging
import asyncio
import traceback as tb

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_HOST,
    CONF_PASSWORD,
    CONF_SCAN_INTERVAL,
    CONF_USERNAME,
)
from homeassistant.core import DOMAIN, HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.typing import StateType
from homeassistant.helpers.entity import DeviceInfo

from .api import RouterAPI, RouterAPIAuthError
from .const import (DEFAULT_SCAN_INTERVAL,
                    EP_CELLINFO,
                    EP_DEVICESTATUS,
                    EP_LANINFO,
                    EP_TRAFFIC,
                    EP_COMMON,
                    API_SCHEMA)

_LOGGER = logging.getLogger(__name__)


@dataclass
class RouterAPIData:
    """Class to hold api data."""

    data: dict


class RouterCoordinator(DataUpdateCoordinator):
    """My example coordinator."""

    data: RouterAPIData

    def __init__(self, hass: HomeAssistant,
                 config_entry: ConfigEntry) -> None:
        """Initialize coordinator."""

        # Set variables from values entered in config flow setup
        self.host = config_entry.data[CONF_HOST]
        self.user = config_entry.data[CONF_USERNAME]
        self.pwd = config_entry.data[CONF_PASSWORD]

        self.device_info = None
        self.config_entry = config_entry

        # set variables from options.  You need a default here incase options have not been set
        self.poll_interval = config_entry.options.get(
            CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
        )

        # Initialise DataUpdateCoordinator
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN} ({config_entry.unique_id})",
            # Method to call on every update interval.
            update_method=self.async_update_data,
            # Polling interval. Will only be polled if there are subscribers.
            # Using config option here but you can just use a value.
            update_interval=timedelta(seconds=self.poll_interval),
        )

        session = async_get_clientsession(
            hass=hass,
            verify_ssl=False
        )

        session.cookie_jar._unsafe = True

        # Initialise your api here
        self.api = RouterAPI(host=self.host,
                             user=self.user,
                             pwd=self.pwd,
                             session=session)

    async def async_update_data(self):
        """Fetch data from API endpoint.

        This is the place to pre-process the data to lookup tables
        so entities can quickly look up their data.
        """
        try:
            # First login to refresh session
            if await self.api.async_login():
                # Get API endpoints
                endpoints = [EP_CELLINFO,
                             EP_DEVICESTATUS,
                             EP_LANINFO,
                             EP_TRAFFIC,
                             EP_COMMON]
                
                results = await asyncio.gather(
                    *[self.api.async_query_api(oid=endpoint) for endpoint in endpoints],
                    return_exceptions=True)
                
                data = {
                    endpoints[i]: results[i]
                    for i in range(len(endpoints))
                }

                info = data[EP_DEVICESTATUS]['DeviceInfo']

                self.device_info = DeviceInfo(
                    configuration_url=f'{API_SCHEMA}://{self.api.host}',
                    identifiers={(DOMAIN, self.config_entry.entry_id)},
                    model=info['ModelName'],
                    manufacturer=info['Manufacturer'],
                    name=info['Description'],
                    sw_version=info['SoftwareVersion'],
                    hw_version=info['HardwareVersion'],
                    model_id=info['ProductClass'],
                    serial_number=['SerialNumber'],
                )

                return data

        except RouterAPIAuthError as err:
            _LOGGER.error(err)
            raise UpdateFailed(err) from err
        except Exception as err:
            # This will show entities as unavailable by raising UpdateFailed exception
            _LOGGER.error(''.join(tb.format_exception(None, err, err.__traceback__)))
            _LOGGER.error(err)
            raise UpdateFailed(f"Error communicating with API: {err}") from err

        # # What is returned here is stored in self.data by the DataUpdateCoordinator
        # return RouterAPIData(self.api.controller_name, devices)

    def get_value(self, endpoint: str, path: list[int | str], default=None) -> StateType:
        """
        Get a value from the data by a given path.
        When the value is absent, the default (None) will be returned and an error will be logged.
        """
        value = self.data.get(endpoint, default)

        try:
            for key in path:
                value = value[key]

            value_type = type(value).__name__

            if value_type in ["int", "float", "str"]:
                _LOGGER.debug(
                    "Path %s returns a %s (value = %s)", path, value_type, value
                )
            else:
                _LOGGER.debug("Path %s returns a %s", path, value_type)

            return value
        except (IndexError, KeyError):
            _LOGGER.warning("Can't find a value for %s in the API response", path)
            return default
