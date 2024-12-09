import asyncio
from abc import ABC, abstractmethod

from aiohttp import ClientSession

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

    @abstractmethod
    def to_dict(self) -> dict[str, str]:
        """Return the state of the LinkPlayEndpoint"""


class LinkPlayApiEndpoint(LinkPlayEndpoint):
    """Represents a LinkPlay HTTP API endpoint."""

    def __init__(
        self, *, protocol: str, port: int, endpoint: str, session: ClientSession
    ):
        assert protocol in [
            "http",
            "https",
        ], "Protocol must be either 'http' or 'https'"
        if (protocol == "http" and port != 80) or (protocol == "https" and port != 443):
            self._endpoint: str = f"{protocol}://{endpoint}:{port}"
        else:
            self._endpoint: str = f"{protocol}://{endpoint}"

        self._session: ClientSession = session

    def to_dict(self):
        """Return the state of the LinkPlayEndpoint"""
        return {"endpoint": self._endpoint}

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

    def __init__(
        self, *, connection: tuple[asyncio.StreamReader, asyncio.StreamWriter]
    ):
        self._connection = connection

    def to_dict(self):
        """Return the state of the LinkPlayEndpoint"""
        return {}

    async def request(self, command: str) -> None:
        reader, writer = self._connection
        await call_tcpuart(reader, writer, command)

    async def json_request(self, command: str) -> dict[str, str]:
        reader, writer = self._connection
        return await call_tcpuart_json(reader, writer, command)
