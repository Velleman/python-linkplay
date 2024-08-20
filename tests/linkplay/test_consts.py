import pytest

from linkplay.consts import INPUT_MODE_MAP, PLAY_MODE_SEND_MAP, InputMode, PlayingMode


def test_ensure_input_mode_has_mapping() -> None:
    """Ensure every InputMode is in INPUT_MODE_MAP."""
    for input_mode in InputMode:
        assert input_mode in INPUT_MODE_MAP


@pytest.mark.skip(reason="Not every playing mode is mapped yet.")
def test_ensure_playing_mode_has_mapping() -> None:
    """Ensure every PlayingMode is in PLAY_MODE_SEND_MAP."""
    for playing_mode in PlayingMode:
        assert playing_mode in PLAY_MODE_SEND_MAP
