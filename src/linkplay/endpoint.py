import asyncio
from abc import ABC, abstractmethod
from typing import Tuple

from aiohttp import ClientSession

from linkplay.consts import TCPPORT
from linkplay.utils import (
    call_tcpuart,
    call_tcpuart_json,
    session_call_api_json,
    session_call_api_ok,
)


class LinkPlayEndpoint(ABC):
    """Represents an abstract LinkPlay endpoint."""

    @abstractmethod
    async def request(self, command: str) -> None:
        """Performs a request on the given command and verifies the result."""

    @abstractmethod
    async def json_request(self, command: str) -> dict[str, str]:
        """Performs a request on the given command and returns the result as a JSON object."""


class LinkPlayApiEndpoint(LinkPlayEndpoint):
    """Represents a LinkPlay HTTP API endpoint."""

    def __init__(self, *, protocol: str, endpoint: str, session: ClientSession):
        assert protocol in [
            "http",
            "https",
        ], "Protocol must be either 'http' or 'https'"
        self._endpoint: str = f"{protocol}://{endpoint}"
        self._session: ClientSession = session

    async def request(self, command: str) -> None:
        """Performs a GET request on the given command and verifies the result."""
        await session_call_api_ok(self._endpoint, self._session, command)

    async def json_request(self, command: str) -> dict[str, str]:
        """Performs a GET request on the given command and returns the result as a JSON object."""
        return await session_call_api_json(self._endpoint, self._session, command)

    def __str__(self) -> str:
        return self._endpoint


class LinkPlayTcpUartEndpoint(LinkPlayEndpoint):
    """Represents a LinkPlay TCPUART API endpoint."""

    def __init__(self, *, endpoint: str):
        self._host: str = endpoint
        self._port = TCPPORT
        self._connection: Tuple[asyncio.StreamReader, asyncio.StreamWriter] | None = (
            None
        )

    async def request(self, command: str) -> None:
        if self._connection is None:
            self._connection = await asyncio.open_connection(self._host, self._port)
        reader, writer = self._connection

        await call_tcpuart(reader, writer, command)

    async def json_request(self, command: str) -> dict[str, str]:
        if self._connection is None:
            self._connection = await asyncio.open_connection(self._host, self._port)
        reader, writer = self._connection
        return await call_tcpuart_json(reader, writer, command)

    async def close_connection(self) -> None:
        """Closes a TCP connection."""
        if self._connection is not None:
            reader, writer = self._connection
            writer.close()
            await writer.wait_closed()
            self._connection = None

    def __str__(self) -> str:
        return self._host
