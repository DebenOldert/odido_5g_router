"""ZYXEL API Client"""

import asyncio
import base64

import aiohttp

from .const import (API_TIMEOUT,
                    API_SCHEMA,
                    API_BASE_PATH,
                    API_LOGIN_PATH,
                    LOGIN_PAYLOAD,
                    KEY_RESULT,
                    VAL_SUCCES,
                    KEY_OBJECT)


class RouterApiClientError(Exception):
    """Exception to indicate a general API error."""


class RouterApiClientCommunicationError(RouterApiClientError):
    """Exception to indicate a communication error."""


class RouterApiClientLoginError(RouterApiClientError):
    """Exception to indicate an api key error."""


class RouterApiClientResponseError(RouterApiClientError):
    """Exception to indicate a response error."""


class RouterApiClient:
    """Router API wrapper for ZYXEL routers"""

    def __init__(
        self,
        endpoint: str,
        user: str,
        password: str,
        session: aiohttp.ClientSession,
    ) -> None:
        """ZYXEL API Client."""
        self.endpoint = endpoint
        self.user = user
        self.password = password
        self._session = session

    async def async_login(self) -> bool:
        """Login and obtain the session cookie"""

        payload = LOGIN_PAYLOAD.copy()
        payload['Input_Account'] = self.user
        payload['Input_Passwd'] = base64.b64encode(
            self.password.encode('utf-8')).decode('utf-8')

        response = await self._session.post(
            f'{API_SCHEMA}://{self.endpoint}{API_LOGIN_PATH}',
            json=payload)
        
        if response.ok:
            try:
                data = response.json()

                if 'result' in data:
                    if data['result'] == 'ZCFG_SUCCESS':
                        return True
                    else:
                        raise RouterApiClientLoginError('Login failed')
                else:
                    raise RouterApiClientResponseError('Key "result" not set in response')
                    
            except Exception as json_exception:
                raise RouterApiClientResponseError(f'Unable to decode login response') \
                    from json_exception
            
        raise RouterApiClientCommunicationError(
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
                            raise RouterApiClientResponseError(f'Response returned error')

                    except Exception as json_exception:
                        raise RouterApiClientResponseError(f'Unable to decode JSON') \
                            from json_exception
                else:
                    raise RouterApiClientCommunicationError(
                        f'Error retrieving API. Status: {response.status}')

        except Exception as exception:
            raise RouterApiClientCommunicationError('Unable to connect to router API') \
                from exception
