"""API Placeholder.

You should create your api seperately and have it hosted on PYPI.  This is included here for the sole purpose
of making this example code executable.
"""

import logging
import base64
import aiohttp
import asyncio

from .const import (API_SCHEMA,
                    API_LOGIN_PATH,
                    API_BASE_PATH,
                    API_TIMEOUT,
                    LOGIN_PAYLOAD,
                    KEY_RESULT,
                    KEY_OBJECT,
                    VAL_SUCCES)

_LOGGER = logging.getLogger(__name__)


class RouterAPI:
    """Class for example API."""

    def __init__(self,
                 host: str,
                 user: str,
                 pwd: str,
                 session: aiohttp) -> None:
        """Initialise."""
        self.host = host
        self.user = user
        self.pwd = pwd
        self.session: aiohttp = session
    
    async def async_login(self) -> bool:
        """Login and obtain the session cookie"""

        payload = LOGIN_PAYLOAD.copy()
        payload['Input_Account'] = self.user
        payload['Input_Passwd'] = base64.b64encode(
            self.password.encode('utf-8')).decode('utf-8')

        response = await self._session.post(
            f'{API_SCHEMA}://{self.ip}{API_LOGIN_PATH}',
            json=payload)
        
        if response.ok:
            try:
                data = response.json()

                if 'result' in data:
                    if data['result'] == VAL_SUCCES:
                        return True
                    else:
                        raise RouterAPIAuthError('Login failed')
                else:
                    raise RouterAPIInvalidResponse('Key "result" not set in response')
                    
            except Exception as json_exception:
                raise RouterAPIInvalidResponse(f'Unable to decode login response') \
                    from json_exception
            
        raise RouterAPIConnectionError(
            f'Error connecting to router. Status: {response.status}')
    
    async def async_query_api(self,
                              oid: str) -> dict:
        """Query an authenticated API endpoint"""
        try:
            async with asyncio.timeout(API_TIMEOUT):
                response = await self._session.get(
                    f'{API_SCHEMA}://{self.endpoint}{API_BASE_PATH}',
                    params={'oid': oid})

                if response.ok:
                    try:
                        data: dict = await response.json()

                        if data.get(KEY_RESULT, None) == VAL_SUCCES:
                            return data.get(KEY_OBJECT, [{}])[0]
                        else:
                            raise RouterAPIInvalidResponse(f'Response returned error')

                    except Exception as json_exception:
                        raise RouterAPIInvalidResponse(f'Unable to decode JSON') \
                            from json_exception
                else:
                    raise RouterAPIConnectionError(
                        f'Error retrieving API. Status: {response.status}')

        except Exception as exception:
            raise RouterAPIConnectionError('Unable to connect to router API') \
                from exception


    @property
    def controller_name(self) -> str:
        """Return the name of the controller."""
        return self.host.replace(".", "_")


class RouterAPIAuthError(Exception):
    """Exception class for auth error."""


class RouterAPIConnectionError(Exception):
    """Exception class for connection error."""

class RouterAPIInvalidResponse(Exception):
    """Exception class for invalid API response."""