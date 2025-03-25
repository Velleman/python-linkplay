import asyncio
import contextlib
import json
import logging
import os
import socket
import ssl
from concurrent.futures import ThreadPoolExecutor
from http import HTTPStatus

import aiofiles
import async_timeout
from aiohttp import ClientError, ClientSession, TCPConnector
from appdirs import AppDirs
from deprecated import deprecated

from linkplay.consts import (
    API_ENDPOINT,
    API_TIMEOUT,
    MTLS_CERTIFICATE_CONTENTS,
    TCP_MESSAGE_LENGTH,
    EqualizerMode,
    PlayerAttribute,
    PlayingStatus,
)
from linkplay.exceptions import LinkPlayInvalidDataException, LinkPlayRequestException


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
    """Calls the LinkPlay API and returns the result as a JSON object

    Args:
        endpoint (str): The endpoint to use.
        session (ClientSession): The client session to use.
        command (str): The command to use.

    Raises:
        LinkPlayRequestException: Thrown when the request fails (timeout, error http status).
        LinkPlayInvalidDataException: Thrown when the request has succeeded with invalid json.

    Returns:
        str: The response of the API call.
    """
    try:
        result = await session_call_api(endpoint, session, command)
        return json.loads(result)  # type: ignore
    except json.JSONDecodeError as jsonexc:
        url = API_ENDPOINT.format(endpoint, command)
        raise LinkPlayInvalidDataException(
            f"Unexpected JSON ({result}) received from '{url}'"
        ) from jsonexc


async def session_call_api_ok(
    endpoint: str, session: ClientSession, command: str
) -> None:
    """Calls the LinkPlay API and checks if the response is OK. Throws exception if not."""
    result = await session_call_api(endpoint, session, command)

    if result != "OK":
        raise LinkPlayRequestException(f"Didn't receive expected OK from {endpoint}")


async def call_tcpuart(
    reader: asyncio.StreamReader, writer: asyncio.StreamWriter, cmd: str
) -> str:
    """Get the latest data from TCP UART service."""
    payload_header: str = "18 96 18 20 "
    payload_length: str = format(len(cmd), "02x")
    payload_command_header: str = " 00 00 00 c1 02 00 00 00 00 00 00 00 00 00 00 "
    payload_command_content: str = " ".join(hex(ord(c))[2:] for c in cmd)

    async with async_timeout.timeout(API_TIMEOUT):
        writer.write(
            bytes.fromhex(
                payload_header
                + payload_length
                + payload_command_header
                + payload_command_content
            )
        )

        data: bytes = await reader.read(TCP_MESSAGE_LENGTH)

        if data == b"":
            raise LinkPlayRequestException("No data received from socket")

        return str(repr(data))


async def call_tcpuart_json(
    reader: asyncio.StreamReader, writer: asyncio.StreamWriter, cmd: str
) -> dict[str, str]:
    """Get JSON data from TCPUART service."""
    raw_response: str = await call_tcpuart(reader, writer, cmd)
    strip_start = raw_response.find("{")
    strip_end = raw_response.find("}", strip_start) + 1
    data = raw_response[strip_start:strip_end]
    return json.loads(data)  # type: ignore


def decode_hexstr(hexstr: str) -> str:
    """Decode a hex string."""
    try:
        return bytes.fromhex(hexstr).decode("utf-8")
    except ValueError:
        return hexstr


@deprecated(version="0.0.9", reason="Use async_create_unverified_context instead")
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


async def async_create_unverified_context(
    executor: ThreadPoolExecutor | None = None,
) -> ssl.SSLContext:
    """Asynchronously creates an unverified SSL context with the default mTLS certificate."""
    async with aiofiles.tempfile.NamedTemporaryFile(
        "w", encoding="utf-8"
    ) as mtls_certificate:
        await mtls_certificate.write(MTLS_CERTIFICATE_CONTENTS)
        await mtls_certificate.flush()
        certfile: str = str(mtls_certificate.name)
        return await async_create_ssl_context(certfile=certfile, executor=executor)


async def async_create_ssl_context(
    *, certfile: str, executor: ThreadPoolExecutor | None = None
) -> ssl.SSLContext:
    """Creates an SSL context from given certificate file."""
    sslcontext: ssl.SSLContext = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    sslcontext.check_hostname = False
    sslcontext.verify_mode = ssl.CERT_NONE

    loop = asyncio.get_running_loop()
    await loop.run_in_executor(executor, sslcontext.load_cert_chain, certfile)

    with contextlib.suppress(AttributeError):
        # This only works for OpenSSL >= 1.0.0
        sslcontext.options |= ssl.OP_NO_COMPRESSION
    await loop.run_in_executor(executor, sslcontext.set_default_verify_paths)
    return sslcontext


@deprecated(version="0.0.9", reason="Use async_create_ssl_context instead")
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


@deprecated(
    version="0.0.9", reason="Use async_create_unverified_client_session instead"
)
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


def equalizer_mode_to_number_mapping(equalizer_mode: EqualizerMode) -> str | None:
    """Converts EqualizerMode to a number mapping."""
    match equalizer_mode:
        case EqualizerMode.NONE:
            return "0"
        case EqualizerMode.CLASSIC:
            return "1"
        case EqualizerMode.POP:
            return "2"
        case EqualizerMode.JAZZ:
            return "3"
        case EqualizerMode.VOCAL:
            return "4"
    return None


def equalizer_mode_from_number_mapping(value: str | None) -> EqualizerMode | None:
    """Converts a number mapping to EqualizerMode."""
    match value:
        case "0":
            return EqualizerMode.NONE
        case "1":
            return EqualizerMode.CLASSIC
        case "2":
            return EqualizerMode.POP
        case "3":
            return EqualizerMode.JAZZ
        case "4":
            return EqualizerMode.VOCAL
    return None
