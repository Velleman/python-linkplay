from linkplay.bridge import LinkPlayBridge


def test_endpoint():
    """Tests if the endpoint is correctly constructed."""
    bridge = LinkPlayBridge("http", "1.2.3.4", None)
    assert "http://1.2.3.4" == bridge.endpoint
