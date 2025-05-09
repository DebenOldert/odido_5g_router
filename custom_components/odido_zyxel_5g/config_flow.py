"""Adds config flow for ZYXEL."""

import logging
from typing import Any

from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    FlowResult,
    OptionsFlow,
)
from homeassistant.const import (
    CONF_NAME,
    CONF_SCAN_INTERVAL,
    CONF_USERNAME,
    CONF_PASSWORD,
    CONF_IP_ADDRESS
)
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_create_clientsession
import homeassistant.helpers.config_validation as cv
import voluptuous as vol

from .api import (
    RouterApiClient,
    RouterApiClientError,
    RouterApiClientLoginError,
    RouterApiClientCommunicationError,
    RouterApiClientResponseError,
)
from .const import (DEFAULT_SCAN_INTERVAL,
                    DOMAIN,
                    DEFAULT_IP,
                    DEFAULT_USER)

_LOGGER: logging.Logger = logging.getLogger(__package__)


class RouterFlowHandler(ConfigFlow, domain=DOMAIN):
    """Config flow for Odido Router."""

    VERSION = 2

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle a flow initialized by the user."""
        _errors = {}
        if user_input is not None:
            try:
                await self._validate_user_input(
                    user_input[CONF_IP_ADDRESS],
                    user_input[CONF_USERNAME],
                    user_input[CONF_PASSWORD],
                )
            except RouterApiClientCommunicationError as exception:
                _LOGGER.error(exception)
                _errors["base"] = "general"
            except RouterApiClientLoginError as exception:
                _LOGGER.error(exception)
                _errors["base"] = "api_key"
            except RouterApiClientResponseError as exception:
                _LOGGER.error(exception)
                _errors["base"] = "daily_limit"
            else:
                return self.async_create_entry(
                    title=user_input[CONF_NAME], data=user_input
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_IP_ADDRESS, default=DEFAULT_IP
                    ): str,
                    vol.Required(
                        CONF_USERNAME, default=DEFAULT_USER
                    ): str,
                    vol.Required(CONF_PASSWORD): str
                }
            ),
            errors=_errors,
        )

    async def _validate_user_input(self, endpoint: str, user: str, password: str):
        """Validate user input."""
        session = async_create_clientsession(self.hass)
        client = RouterApiClient(endpoint=endpoint,
                                 user=user,
                                 password=password,
                                 session=session)
        await client.async_login()

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        return RouterOptionsFlowHandler()


class RouterOptionsFlowHandler(OptionsFlow):
    """Router config flow options handler."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(
                title=self.config_entry.data.get(CONF_NAME), data=user_input
            )

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_SCAN_INTERVAL,
                        default=self.config_entry.options.get(
                            CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
                        ),
                    ): vol.All(vol.Coerce(int), vol.Range(min=30, max=3600))
                }
            ),
        )