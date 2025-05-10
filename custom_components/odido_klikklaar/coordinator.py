"""Integration 101 Template integration using DataUpdateCoordinator."""

from dataclasses import dataclass
from datetime import timedelta
import logging
import asyncio

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

from .api import RouterAPI, APIAuthError, Device, DeviceType
from .const import (DEFAULT_SCAN_INTERVAL,
                    EP_CELLINFO,
                    EP_DEVICESTATUS,
                    EP_LANINFO)

_LOGGER = logging.getLogger(__name__)


@dataclass
class RouterAPIData:
    """Class to hold api data."""

    data: dict


class RouterCoordinator(DataUpdateCoordinator):
    """My example coordinator."""

    data: RouterAPIData

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry) -> None:
        """Initialize coordinator."""

        # Set variables from values entered in config flow setup
        self.host = config_entry.data[CONF_HOST]
        self.user = config_entry.data[CONF_USERNAME]
        self.pwd = config_entry.data[CONF_PASSWORD]

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
                             EP_LANINFO]
                
                results = await asyncio.gather(
                    *[self.api.async_query_api(oid=endpoint) for endpoint in endpoints],
                    return_exceptions=True)
                
                return RouterAPIData({
                    endpoints[i]: results[i]
                    for i in len(endpoints)
                })

        except APIAuthError as err:
            _LOGGER.error(err)
            raise UpdateFailed(err) from err
        except Exception as err:
            # This will show entities as unavailable by raising UpdateFailed exception
            raise UpdateFailed(f"Error communicating with API: {err}") from err

        # # What is returned here is stored in self.data by the DataUpdateCoordinator
        # return RouterAPIData(self.api.controller_name, devices)
