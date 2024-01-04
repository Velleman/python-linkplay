import asyncio
from asyncio import CancelledError
import async_timeout
from aiohttp import ClientSession, ClientError
from http import HTTPStatus

from linkplay.consts import API_ENDPOINT, API_TIMEOUT
from linkplay.exceptions import LinkPlayRequestException


async def session_call_api(endpoint: str, session: ClientSession, command: str):
    url = API_ENDPOINT.format(endpoint, command)

    try:
        async with async_timeout.timeout(API_TIMEOUT):
            response = await session.get(url, ssl=False)

    except (asyncio.TimeoutError, ClientError, CancelledError) as error:
        raise LinkPlayRequestException("Error requesting data from LinkPlayDevice (httpapi) '{}': {}".format(url, error)) from error

    if response.status == HTTPStatus.OK:
        return await response.text()

    raise LinkPlayRequestException("Error requesting data from LinkPlayDevice (httpapi) '{}': {} / {}".format(url, response.status, response))
