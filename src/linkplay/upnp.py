import xml.etree.ElementTree as ET

import validators
from aiohttp import ClientSession
from async_upnp_client.aiohttp import AiohttpSessionRequester
from async_upnp_client.client import UpnpDevice
from async_upnp_client.client_factory import UpnpFactory

from linkplay.consts import LOGGER

UPNP_TIMEOUT = 2

XML_DESCRIPTION_ENDPOINT: str = "{}/description.xml"


class LinkPlayUPNPUpdateResponse:
    """Represents a response from LinkPlayUPNPUpdateResponse."""

    _trackc: str = None
    _media_uri_final: str = None
    _media_title: str = None
    _media_album: str = None
    _media_artist: str = None
    _media_image_url: str = None

    def __init__(
        self,
        trackc: str,
        media_uri_final: str,
        media_title: str = None,
        media_album: str = None,
        media_artist: str = None,
        media_image_url: str = None,
    ):
        self._trackc = trackc
        self._media_uri_final = media_uri_final
        self._media_title = media_title
        self._media_album = media_album
        self._media_artist = media_artist
        self._media_image_url = media_image_url


class LinkPlayUPNPUtility:
    """Represents a utility class to handle upnp."""

    def __init__(
        self, *, protocol: str, port: int, endpoint: str, session: ClientSession
    ):
        assert protocol in [
            "http",
            "https",
        ], "Protocol must be either 'http' or 'https'"

        self._endpoint: str = f"{protocol}://{endpoint}:49152"
        self._session: ClientSession = session

        requester = AiohttpSessionRequester(session=self._session, timeout=UPNP_TIMEOUT)
        self._factory = UpnpFactory(requester)
        self._upnp_device = None

    async def _fetch_device(self) -> UpnpDevice:
        """Fetches the UPnP device description."""
        if self._upnp_device is None:
            url = XML_DESCRIPTION_ENDPOINT.format(self._endpoint)
            try:
                self._upnp_device = await self._factory.async_create_device(url)
            except Exception as error:
                LOGGER.warning(
                    "Failed communicating with LinkPlayDevice (UPnP) '%s': %s",
                    self._endpoint,
                    error,
                )
        return self._upnp_device

    async def async_update_via_upnp(self) -> LinkPlayUPNPUpdateResponse:
        """Update track info via UPNP."""

        if self._upnp_device is None:
            await self._fetch_device()

        _service = self._upnp_device.service(
            "urn:schemas-upnp-org:service:AVTransport:1"
        )
        LOGGER.debug("Fetching %s for UPNP service: %s", self._endpoint, _service)

        media_info = dict()
        media_metadata = None
        try:
            media_info = await _service.action("GetMediaInfo").async_call(InstanceID=0)
            _trackc = media_info.get("CurrentURI")
            _media_uri_final = media_info.get("TrackSource")
            media_metadata = media_info.get("CurrentURIMetaData")
            LOGGER.debug(
                "Fetching %s for UPNP media_metadata: %s",
                self._endpoint,
                media_info,
            )
        except Exception as error:
            LOGGER.warning(
                "Fetching %s for GetMediaInfo failed: %s", self._endpoint, error
            )

        if media_metadata is None:
            return LinkPlayUPNPUpdateResponse(
                trackc=_trackc,
                media_uri_final=_media_uri_final,
            )

        xml_tree = ET.fromstring(media_metadata)

        xml_path = "{urn:schemas-upnp-org:metadata-1-0/DIDL-Lite/}item/"
        title_xml_path = "{http://purl.org/dc/elements/1.1/}title"
        artist_xml_path = "{urn:schemas-upnp-org:metadata-1-0/upnp/}artist"
        album_xml_path = "{urn:schemas-upnp-org:metadata-1-0/upnp/}album"
        image_xml_path = "{urn:schemas-upnp-org:metadata-1-0/upnp/}albumArtURI"
        radiosub_xml_path = "{http://purl.org/dc/elements/1.1/}subtitle"

        _media_title = xml_tree.find("{0}{1}".format(xml_path, title_xml_path)).text
        _media_artist = xml_tree.find("{0}{1}".format(xml_path, artist_xml_path)).text
        _media_album = xml_tree.find("{0}{1}".format(xml_path, album_xml_path)).text
        _media_image_url = xml_tree.find("{0}{1}".format(xml_path, image_xml_path)).text

        if not validators.url(_media_image_url):
            _media_image_url = None

        return LinkPlayUPNPUpdateResponse(
            trackc=_trackc,
            media_uri_final=_media_uri_final,
            media_title=_media_title,
            media_album=_media_album,
            media_artist=_media_artist,
            media_image_url=_media_image_url,
        )
