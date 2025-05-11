"""Constants for Odido Klik&Klaar 5G router"""

from typing import Final

# API
API_SCHEMA: Final[str] = 'https'
API_BASE_PATH: Final[str] = '/cgi-bin/DAL'
API_LOGIN_PATH: Final[str] = '/UserLogin'
API_TIMEOUT: Final = 10
API_TIMEZONE: Final = "Europe/Amsterdam"

# Endpoints
EP_CELLINFO: Final[str] = 'status'
EP_LANINFO: Final[str] = 'lanhosts'
EP_DEVICESTATUS: Final[str] = 'cardpage_status'
EP_TRAFFIC: Final[str] = 'Traffic_Status'
EP_COMMON: Final[str] = 'cardpage_status'

# Keys & values
KEY_RESULT: Final[str] = 'result'
KEY_OBJECT: Final[str] = 'Object'
VAL_SUCCES: Final[str] = 'ZCFG_SUCCESS'

# Base component constants.
DOMAIN: Final = "odido"
NAME: Final = "ZYXEL"
SUPPLIER: Final = "Odido"
VERSION: Final = "0.0.1"

# Defaults
DEFAULT_IP: Final[str] = '192.168.1.1'
DEFAULT_USER: Final[str] = 'admin'
DEFAULT_NAME: Final[str] = NAME
DEFAULT_SCAN_INTERVAL: Final = 60
MIN_SCAN_INTERVAL = 30

# Payloads
LOGIN_PAYLOAD: dict = {
    'Input_Account': None,
    'Input_Passwd': None,
    'currLang': 'en',
    'RememberPassword': 0,
    'SHA512_password': False
}
