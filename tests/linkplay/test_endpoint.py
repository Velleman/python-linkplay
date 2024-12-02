"""Test endpoint functionality."""

import pytest

from linkplay.endpoint import LinkPlayApiEndpoint


def test_api_endpoint_protocol_raises_assertion_error() -> None:
    """Tests whether or not instantiating the LinkPlayApiEndpoint
    with an invalid protocol raises an AssertionError."""

    with pytest.raises(AssertionError):
        LinkPlayApiEndpoint(protocol="ftp", port=21, endpoint="1.2.3.4", session=None)
