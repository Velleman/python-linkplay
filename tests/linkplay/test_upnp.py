"""Test UPnP album art retrieval."""

from unittest.mock import AsyncMock, MagicMock, patch

from async_upnp_client.exceptions import UpnpError
from linkplay.upnp import LinkPlayUPnP, _is_url, _parse_metadata

# A real DIDL-Lite document as returned by an Arylic/Audio Pro device playing
# Spotify (album art is a fully-qualified Spotify CDN url).
DIDL_WITH_ART = (
    '<DIDL-Lite xmlns:dc="http://purl.org/dc/elements/1.1/" '
    'xmlns:upnp="urn:schemas-upnp-org:metadata-1-0/upnp/" '
    'xmlns:song="www.wiimu.com/song/" '
    'xmlns="urn:schemas-upnp-org:metadata-1-0/DIDL-Lite/">'
    '<item id="0">'
    "<dc:title>La thune de ma femme</dc:title>"
    "<upnp:artist>Hippocampe Fou</upnp:artist>"
    "<upnp:album>Consumed In Key</upnp:album>"
    "<upnp:albumArtURI>https://i.scdn.co/image/ab67616d0000b273a7</upnp:albumArtURI>"
    "</item></DIDL-Lite>"
)

# What a follower / idle device reports: the placeholder "un_known".
DIDL_UNKNOWN_ART = (
    '<DIDL-Lite xmlns:dc="http://purl.org/dc/elements/1.1/" '
    'xmlns:upnp="urn:schemas-upnp-org:metadata-1-0/upnp/" '
    'xmlns="urn:schemas-upnp-org:metadata-1-0/DIDL-Lite/">'
    '<item id="0"><dc:title></dc:title>'
    "<upnp:albumArtURI>un_known</upnp:albumArtURI></item></DIDL-Lite>"
)


def test_parse_metadata_with_art():
    """A valid DIDL document yields all fields and keeps the art url."""
    metadata = _parse_metadata(DIDL_WITH_ART)
    assert metadata.title == "La thune de ma femme"
    assert metadata.artist == "Hippocampe Fou"
    assert metadata.album == "Consumed In Key"
    assert metadata.album_art_uri == "https://i.scdn.co/image/ab67616d0000b273a7"


def test_parse_metadata_discards_placeholder_art():
    """The 'un_known' placeholder is not a url and is discarded."""
    metadata = _parse_metadata(DIDL_UNKNOWN_ART)
    assert metadata.album_art_uri is None
    assert metadata.title is None


def test_parse_metadata_malformed():
    """Malformed XML yields empty metadata instead of raising."""
    metadata = _parse_metadata("<not-valid")
    assert metadata.album_art_uri is None


def test_parse_metadata_without_item():
    """A document without an <item> yields empty metadata."""
    metadata = _parse_metadata(
        '<DIDL-Lite xmlns="urn:schemas-upnp-org:metadata-1-0/DIDL-Lite/"></DIDL-Lite>'
    )
    assert metadata.title is None
    assert metadata.album_art_uri is None


def test_is_url():
    """Only absolute urls are accepted."""
    assert _is_url("https://i.scdn.co/image/abc")
    assert not _is_url("un_known")
    assert not _is_url("")


async def test_async_get_metadata_returns_parsed():
    """GetMediaInfo metadata is parsed into a LinkPlayUPnPMetadata."""
    upnp = LinkPlayUPnP("1.2.3.4", session=AsyncMock())
    service = MagicMock()
    service.action.return_value.async_call = AsyncMock(
        return_value={"CurrentURIMetaData": DIDL_WITH_ART}
    )
    with patch.object(
        LinkPlayUPnP, "_async_get_service", AsyncMock(return_value=service)
    ):
        metadata = await upnp.async_get_metadata()

    assert metadata is not None
    assert metadata.album_art_uri == "https://i.scdn.co/image/ab67616d0000b273a7"


async def test_async_get_metadata_no_service():
    """No AVTransport service yields None."""
    upnp = LinkPlayUPnP("1.2.3.4", session=AsyncMock())
    with patch.object(LinkPlayUPnP, "_async_get_service", AsyncMock(return_value=None)):
        assert await upnp.async_get_metadata() is None


async def test_async_get_metadata_action_error():
    """A UPnP error while calling GetMediaInfo yields None."""
    upnp = LinkPlayUPnP("1.2.3.4", session=AsyncMock())
    service = MagicMock()
    service.action.return_value.async_call = AsyncMock(side_effect=UpnpError())
    with patch.object(
        LinkPlayUPnP, "_async_get_service", AsyncMock(return_value=service)
    ):
        assert await upnp.async_get_metadata() is None
