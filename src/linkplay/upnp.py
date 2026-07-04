"""UPnP AVTransport helper for LinkPlay devices.

Some LinkPlay devices (e.g. several Audio Pro and Arylic models) do not expose
album art through the HTTP API, and a few do not expose ``getPlayerStatusEx``
at all. The information is however available through the device's UPnP
AVTransport service, which this module retrieves as a fallback.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from urllib.parse import urlparse
from xml.etree.ElementTree import Element, ParseError

from aiohttp import ClientError, ClientSession
from async_upnp_client.aiohttp import AiohttpSessionRequester
from async_upnp_client.client import UpnpDevice, UpnpService
from async_upnp_client.client_factory import UpnpFactory
from async_upnp_client.exceptions import UpnpError
from defusedxml.common import DefusedXmlException
from defusedxml.ElementTree import fromstring

from linkplay.consts import LOGGER

UPNP_PORT: int = 49152
UPNP_TIMEOUT: int = 2
AVTRANSPORT_SERVICE: str = "urn:schemas-upnp-org:service:AVTransport:1"
DESCRIPTION_URL: str = "http://{host}:{port}/description.xml"

_DIDL_NAMESPACES: dict[str, str] = {
    "didl": "urn:schemas-upnp-org:metadata-1-0/DIDL-Lite/",
    "dc": "http://purl.org/dc/elements/1.1/",
    "upnp": "urn:schemas-upnp-org:metadata-1-0/upnp/",
}


@dataclass
class LinkPlayUPnPMetadata:
    """Media metadata retrieved from the UPnP AVTransport service."""

    title: str | None = None
    artist: str | None = None
    album: str | None = None
    album_art_uri: str | None = None


class LinkPlayUPnP:
    """Retrieves media information from a LinkPlay device over UPnP."""

    def __init__(self, host: str, session: ClientSession):
        self._host = host
        self._factory = UpnpFactory(
            AiohttpSessionRequester(session, timeout=UPNP_TIMEOUT)
        )
        self._device: UpnpDevice | None = None

    async def _async_get_service(self) -> UpnpService | None:
        """Return the AVTransport service, creating the device once."""
        if self._device is None:
            url = DESCRIPTION_URL.format(host=self._host, port=UPNP_PORT)
            try:
                self._device = await self._factory.async_create_device(url)
            except (UpnpError, ClientError, asyncio.TimeoutError) as error:
                LOGGER.debug("Failed to reach %s over UPnP: %s", self._host, error)
                return None

        if not self._device.has_service(AVTRANSPORT_SERVICE):
            return None
        return self._device.service(AVTRANSPORT_SERVICE)

    async def async_get_metadata(self) -> LinkPlayUPnPMetadata | None:
        """Return the current media metadata, or None if unavailable."""
        service = await self._async_get_service()
        if service is None:
            return None

        try:
            result = await service.action("GetMediaInfo").async_call(InstanceID=0)
        except (UpnpError, ClientError, asyncio.TimeoutError) as error:
            LOGGER.debug("UPnP GetMediaInfo failed for %s: %s", self._host, error)
            return None

        metadata: str | None = result.get("CurrentURIMetaData")
        if not metadata:
            return None
        return _parse_metadata(metadata)


def _parse_metadata(didl: str) -> LinkPlayUPnPMetadata:
    """Parse a DIDL-Lite metadata document into LinkPlayUPnPMetadata."""
    try:
        root = fromstring(didl)
    except (ParseError, DefusedXmlException):
        return LinkPlayUPnPMetadata()

    item = root.find("didl:item", _DIDL_NAMESPACES)
    if item is None:
        return LinkPlayUPnPMetadata()

    album_art_uri = _find_text(item, "upnp:albumArtURI")
    if album_art_uri is not None and not _is_url(album_art_uri):
        # Devices report placeholders such as "un_known" when no art is known.
        album_art_uri = None

    return LinkPlayUPnPMetadata(
        title=_find_text(item, "dc:title"),
        artist=_find_text(item, "upnp:artist"),
        album=_find_text(item, "upnp:album"),
        album_art_uri=album_art_uri,
    )


def _find_text(item: Element, path: str) -> str | None:
    """Return the stripped text of a child element, or None when empty."""
    element = item.find(path, _DIDL_NAMESPACES)
    if element is None or element.text is None:
        return None
    return element.text.strip() or None


def _is_url(value: str) -> bool:
    """Return whether value is an absolute URL."""
    parsed = urlparse(value)
    return bool(parsed.scheme and parsed.netloc)
