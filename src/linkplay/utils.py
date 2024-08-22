import asyncio
import contextlib
import json
import os
import socket
import ssl
from http import HTTPStatus

import aiofiles
import async_timeout
from aiohttp import ClientError, ClientSession, TCPConnector
from appdirs import AppDirs

from linkplay.consts import (
    API_ENDPOINT,
    API_TIMEOUT,
    MTLS_CERTIFICATE_CONTENTS,
    PlayerAttribute,
    PlayingStatus,
)
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
            response = await session.get(url)

    except (asyncio.TimeoutError, ClientError, asyncio.CancelledError) as error:
        raise LinkPlayRequestException(
            f"{error} error requesting data from '{url}'"
        ) from error

    if response.status != HTTPStatus.OK:
        raise LinkPlayRequestException(
            f"Unexpected HTTPStatus {response.status} received from '{url}'"
        )

    return await response.text()


async def session_call_api_json(
    endpoint: str, session: ClientSession, command: str
) -> dict[str, str]:
    """Calls the LinkPlay API and returns the result as a JSON object."""
    result = await session_call_api(endpoint, session, command)
    return json.loads(result)  # type: ignore


async def session_call_api_ok(
    endpoint: str, session: ClientSession, command: str
) -> None:
    """Calls the LinkPlay API and checks if the response is OK. Throws exception if not."""
    result = await session_call_api(endpoint, session, command)

    if result != "OK":
        raise LinkPlayRequestException(f"Didn't receive expected OK from {endpoint}")


def decode_hexstr(hexstr: str) -> str:
    """Decode a hex string."""
    try:
        return bytes.fromhex(hexstr).decode("utf-8")
    except ValueError:
        return hexstr


def create_unverified_context() -> ssl.SSLContext:
    """Creates an unverified SSL context with the default mTLS certificate."""
    dirs = AppDirs("python-linkplay")
    mtls_certificate_path = os.path.join(dirs.user_data_dir, "linkplay.pem")

    if not os.path.isdir(dirs.user_data_dir):
        os.makedirs(dirs.user_data_dir, exist_ok=True)

    if not os.path.isfile(mtls_certificate_path):
        with open(mtls_certificate_path, "w", encoding="utf-8") as file:
            file.write(MTLS_CERTIFICATE_CONTENTS)

    return create_ssl_context(path=mtls_certificate_path)


async def async_create_unverified_context() -> ssl.SSLContext:
    """Asynchronously creates an unverified SSL context with the default mTLS certificate."""
    async with aiofiles.tempfile.NamedTemporaryFile(
        "w", encoding="utf-8"
    ) as mtls_certificate:
        await mtls_certificate.write(MTLS_CERTIFICATE_CONTENTS)
        await mtls_certificate.flush()
        return create_ssl_context(path=str(mtls_certificate.name))


def create_ssl_context(path: str) -> ssl.SSLContext:
    """Creates an SSL context from given certificate file."""
    sslcontext: ssl.SSLContext = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    sslcontext.check_hostname = False
    sslcontext.verify_mode = ssl.CERT_NONE
    sslcontext.load_cert_chain(certfile=path)
    with contextlib.suppress(AttributeError):
        # This only works for OpenSSL >= 1.0.0
        sslcontext.options |= ssl.OP_NO_COMPRESSION
    sslcontext.set_default_verify_paths()
    return sslcontext


def create_unverified_client_session() -> ClientSession:
    """Creates a ClientSession using the default unverified SSL context"""
    context: ssl.SSLContext = create_unverified_context()
    connector: TCPConnector = TCPConnector(family=socket.AF_UNSPEC, ssl=context)
    return ClientSession(connector=connector)


async def async_create_unverified_client_session() -> ClientSession:
    """Asynchronously creates a ClientSession using the default unverified SSL context"""
    context: ssl.SSLContext = await async_create_unverified_context()
    connector: TCPConnector = TCPConnector(family=socket.AF_UNSPEC, ssl=context)
    return ClientSession(connector=connector)


def fixup_player_properties(
    properties: dict[PlayerAttribute, str],
) -> dict[PlayerAttribute, str]:
    """Fixes up PlayerAttribute in a dict."""
    properties[PlayerAttribute.TITLE] = decode_hexstr(
        properties.get(PlayerAttribute.TITLE, "")
    )
    properties[PlayerAttribute.ARTIST] = decode_hexstr(
        properties.get(PlayerAttribute.ARTIST, "")
    )
    properties[PlayerAttribute.ALBUM] = decode_hexstr(
        properties.get(PlayerAttribute.ALBUM, "")
    )

    # Fixup playing status "none" by setting it to "stopped"
    if (
        properties.get(PlayerAttribute.PLAYING_STATUS, "")
        not in PlayingStatus.__members__.values()
    ):
        properties[PlayerAttribute.PLAYING_STATUS] = PlayingStatus.STOPPED

    return properties
