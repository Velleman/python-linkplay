import asyncio
from typing import Dict
import json
from http import HTTPStatus

import async_timeout
from aiohttp import ClientSession, ClientError

from linkplay.consts import API_ENDPOINT, API_TIMEOUT
from linkplay.exceptions import LinkPlayRequestException


async def session_call_api(endpoint: str, session: ClientSession, command: str) -> str:
    """Calls the LinkPlay API and returns the result as a string.

    Args:
        endpoint (str): The endpoint to use.
        session (ClientSession): The client session to use.
        command (str): The command to use.

    Raises:
        LinkPlayRequestException: Thrown when the request fails or an invalid response is received.

    Returns:
        str: The response of the API call.
    """
    url = API_ENDPOINT.format(endpoint, command)

    try:
        async with async_timeout.timeout(API_TIMEOUT):
            response = await session.get(url, ssl=False)

    except (asyncio.TimeoutError, ClientError, asyncio.CancelledError) as error:
        raise LinkPlayRequestException(f"Error requesting data from '{url}'") from error

    if response.status != HTTPStatus.OK:
        raise LinkPlayRequestException(f"Unexpected HTTPStatus {response.status} received from '{url}'")

    return await response.text()


async def session_call_api_json(endpoint: str, session: ClientSession,
                                command: str) -> Dict[str, str]:
    """Calls the LinkPlay API and returns the result as a JSON object."""
    result = await session_call_api(endpoint, session, command)
    return json.loads(result)  # type: ignore


async def session_call_api_ok(endpoint: str, session: ClientSession, command: str) -> None:
    """Calls the LinkPlay API and checks if the response is OK. Throws exception if not."""
    result = await session_call_api(endpoint, session, command)

    if result != "OK":
        raise LinkPlayRequestException(f"Didn't receive expected OK from {endpoint}")


def decode_hexstr(hexstr: str) -> str:
    """Decode a hex string."""
    return bytes.fromhex(hexstr).decode("utf-8")
