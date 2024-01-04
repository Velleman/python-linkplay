from linkplay.bridge import LinkPlayBridge


def test_endpoint():
    bridge = LinkPlayBridge("http", "1.2.3.4")
    assert "http://1.2.3.4" == bridge.endpoint
