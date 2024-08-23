"""Test utility functions."""

from linkplay.consts import PlayerAttribute, PlayingStatus
from linkplay.utils import decode_hexstr, fixup_player_properties


def test_decode_hexstr():
    """Tests the decode_hexstr function."""
    assert "Unknown" == decode_hexstr("556E6B6E6F776E")


def test_decode_hexstr_invalid():
    """Tests the decode_hexstr function upon invalid input."""
    assert "ABCDEFGHIJKLMNOPQRSTUVWXYZ" == decode_hexstr("ABCDEFGHIJKLMNOPQRSTUVWXYZ")


def test_fixup_player_properties_decodes_hexstr():
    """Tests if the fixup_player_properties function properly fixes the dict."""
    test_dict: dict[PlayerAttribute, str] = {
        PlayerAttribute.ARTIST: "556E6B6E6F776E",
        PlayerAttribute.TITLE: "556E6B6E6F776E",
        PlayerAttribute.ALBUM: "556E6B6E6F776E",
    }

    fixed_dict: dict[PlayerAttribute, str] = fixup_player_properties(test_dict)

    assert fixed_dict[PlayerAttribute.ARTIST] == "Unknown"
    assert fixed_dict[PlayerAttribute.TITLE] == "Unknown"
    assert fixed_dict[PlayerAttribute.ALBUM] == "Unknown"


def test_fixup_player_properties_fixes_playing_status():
    """Tests if the fixup_player_properties function properly fixes the dict."""
    test_dict: dict[PlayerAttribute, str] = {
        PlayerAttribute.PLAYING_STATUS: "none",
    }

    fixed_dict: dict[PlayerAttribute, str] = fixup_player_properties(test_dict)

    assert fixed_dict[PlayerAttribute.PLAYING_STATUS] == PlayingStatus.STOPPED
