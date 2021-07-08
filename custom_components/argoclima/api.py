import asyncio
import logging
import socket

import aiohttp
import async_timeout
from custom_components.argoclima.data import ArgoData
from custom_components.argoclima.device_type import ArgoDeviceType

TIMEOUT = 10


_LOGGER: logging.Logger = logging.getLogger(__package__)

HEADERS = {"Content-type": "text/html"}


class ArgoApiClient:
    def __init__(
        self, type: ArgoDeviceType, host: str, session: aiohttp.ClientSession
    ) -> None:
        self._host = host
        self._port = type.port
        self._session = session

    async def async_sync_data(self, data: ArgoData) -> ArgoData:
        try:
            url = f"http://{self._host}:{self._port}/?HMI={data.to_parameter_string()}&UPD={1 if data.is_update_pending() else 0}"

            async with async_timeout.timeout(TIMEOUT, loop=asyncio.get_event_loop()):
                response = await self._session.get(url, headers=HEADERS)
                data.parse_response_parameter_string(await response.text())
                return data

        except asyncio.TimeoutError as exception:
            _LOGGER.error(
                "Timeout error fetching information from %s - %s",
                url,
                exception,
            )

        except (KeyError, TypeError) as exception:
            _LOGGER.error(
                "Error parsing information from %s - %s",
                url,
                exception,
            )
        except (aiohttp.ClientError, socket.gaierror) as exception:
            _LOGGER.error(
                "Error fetching information from %s - %s",
                url,
                exception,
            )
        except Exception as exception:  # pylint: disable=broad-except
            _LOGGER.error("Something really wrong happened! - %s", exception)
