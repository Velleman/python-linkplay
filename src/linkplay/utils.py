import asyncio
import contextlib
import json
import logging
import os
import socket
import ssl
from http import HTTPStatus
from typing import Dict

import aiofiles
import async_timeout
from aiohttp import ClientError, ClientSession, TCPConnector
from appdirs import AppDirs

from linkplay.consts import (
    API_ENDPOINT,
    API_TIMEOUT,
    MTLS_CERTIFICATE_CONTENTS,
    TCPPORT,
)
from linkplay.exceptions import LinkPlayRequestException

_LOGGER = logging.getLogger(__name__)


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
) -> Dict[str, str]:
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


async def call_tcpuart(host: str, cmd: str) -> str | None:
    """Get the latest data from TCP UART service."""
    LENC = format(len(cmd), '02x')
    HED1 = '18 96 18 20 '
    HED2 = ' 00 00 00 c1 02 00 00 00 00 00 00 00 00 00 00 '
    CMHX = ' '.join(hex(ord(c))[2:] for c in cmd)
    data = None
    _LOGGER.debug("Sending to %s TCP UART command: %s", host, cmd)
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(API_TIMEOUT)
            s.connect((host, TCPPORT))
            s.send(bytes.fromhex(HED1 + LENC + HED2 + CMHX))
            data = str(repr(s.recv(1024))).encode().decode("unicode-escape")

        pos = data.find("AXX")
        if pos == -1:
            pos = data.find("MCU")

        data = data[pos:(len(data)-2)]
        _LOGGER.debug(
            "Received from %s TCP UART command result: %s", host, data)
        try:
            s.close()
        except:
            pass

    except socket.error as ex:
        _LOGGER.debug("Error sending TCP UART command: %s with %s", cmd, ex)
        data = None

    return data


async def call_tcpuart_json(host: str, cmd: str) -> dict[str, str]:
    raw_response = await call_tcpuart(host, cmd)
    if not raw_response:
        return dict()
    strip_start = raw_response.find('{')
    strip_end = raw_response.find('}') + 1
    data = raw_response[strip_start:strip_end]
    return json.loads(data)  # type: ignore


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
