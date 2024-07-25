from linkplay.utils import decode_hexstr


def test_decode_hexstr():
    """Tests the decode_hexstr function."""
    assert "Unknown" == decode_hexstr("556E6B6E6F776E")


def test_decode_hexstr_invalid():
    """Tests the decode_hexstr function upon invalid input."""
    assert "ABCDEFGHIJKLMNOPQRSTUVWXYZ" == decode_hexstr("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
