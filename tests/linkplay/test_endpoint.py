"""Test endpoint functionality."""

import pytest
from linkplay.endpoint import LinkPlayApiEndpoint


@pytest.mark.parametrize(
    "protocol, endpoint, port, expected",
    [
        ("http", "1.2.3.4", 80, "http://1.2.3.4"),
        ("http", "1.2.3.4", 8080, "http://1.2.3.4:8080"),
        ("https", "1.2.3.4", 443, "https://1.2.3.4"),
        ("https", "1.2.3.4", 8443, "https://1.2.3.4:8443"),
    ],
)
def test_api_endpoint_protocol_port_combination(
    protocol, endpoint, port, expected
) -> None:
    """Tests the endpoint creation"""

    endpoint: LinkPlayApiEndpoint = LinkPlayApiEndpoint(
        protocol=protocol, port=port, endpoint=endpoint, session=None
    )
    assert f"{endpoint}" == expected


def test_api_endpoint_protocol_raises_assertion_error() -> None:
    """Tests whether or not instantiating the LinkPlayApiEndpoint
    with an invalid protocol raises an AssertionError."""

    with pytest.raises(AssertionError):
        LinkPlayApiEndpoint(protocol="ftp", port=21, endpoint="1.2.3.4", session=None)
