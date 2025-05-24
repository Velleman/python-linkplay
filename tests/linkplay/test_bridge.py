"""Test bridge functionality."""

from typing import Any
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest
from linkplay.bridge import (
    LinkPlayBridge,
    LinkPlayDevice,
    LinkPlayMultiroom,
    LinkPlayPlayer,
)
from linkplay.consts import (
    PLAY_MODE_SEND_MAP,
    AudioOutputHwMode,
    DeviceAttribute,
    EqualizerMode,
    LinkPlayCommand,
    LoopMode,
    MuteMode,
    PlayerAttribute,
    PlayingMode,
    PlayingStatus,
)
from linkplay.endpoint import LinkPlayApiEndpoint
from linkplay.manufacturers import MANUFACTURER_WIIM


def test_device_name():
    """Tests if the device name is correctly set up."""
    endpoint: LinkPlayApiEndpoint = LinkPlayApiEndpoint(
        protocol="http", port=80, endpoint="1.2.3.4", session=None
    )
    bridge: LinkPlayBridge = LinkPlayBridge(endpoint=endpoint)
    assert f"{bridge}" == "http://1.2.3.4"

    bridge.device.properties[DeviceAttribute.DEVICE_NAME] = "TestDevice"
    assert f"{bridge}" == "TestDevice"


async def test_device_update_status():
    """Tests if the device update status is correctly called."""
    bridge = AsyncMock()
    bridge.json_request.return_value = {DeviceAttribute.UUID: "1234"}
    device = LinkPlayDevice(bridge)

    await device.update_status()

    bridge.json_request.assert_called_once_with(LinkPlayCommand.DEVICE_STATUS)
    assert device.uuid == "1234"


async def test_device_reboot():
    """Tests if the device update is correctly called."""
    bridge = AsyncMock()
    device = LinkPlayDevice(bridge)

    await device.reboot()

    bridge.request.assert_called_once_with(LinkPlayCommand.REBOOT)


async def test_deserialize_device():
    """Test the device to deserialize correctly."""
    bridge = AsyncMock()
    device = LinkPlayDevice(bridge)

    device.to_dict()


async def test_player_update_status():
    """Tests if the player update_status is correctly called."""
    bridge = AsyncMock()
    bridge.json_request.return_value = {}
    player = LinkPlayPlayer(bridge)

    await player.update_status()

    bridge.json_request.assert_called_once_with(LinkPlayCommand.PLAYER_STATUS)


async def test_player_update_status_calls_fixup_player_properties():
    """Tests if the player update_status calls fixup_player_properties."""

    with patch("linkplay.bridge.fixup_player_properties") as fixup_mock:
        bridge = AsyncMock()
        player = LinkPlayPlayer(bridge)

        await player.update_status()

        fixup_mock.assert_called_once()


async def test_player_next():
    """Tests if the player next track is correctly called."""
    bridge = AsyncMock()
    player = LinkPlayPlayer(bridge)

    await player.next()

    bridge.request.assert_called_once_with(LinkPlayCommand.NEXT)


async def test_player_previous():
    """Tests if the player previous track is correctly called."""
    bridge = AsyncMock()
    player = LinkPlayPlayer(bridge)

    await player.previous()

    bridge.request.assert_called_once_with(LinkPlayCommand.PREVIOUS)


async def test_player_play():
    """Tests if the player play is correctly called."""
    bridge = AsyncMock()
    player = LinkPlayPlayer(bridge)

    await player.play("test")

    bridge.request.assert_called_once_with(LinkPlayCommand.PLAY.format("test"))


async def test_player_resume():
    """Tests if the player resume is correctly called."""
    bridge = AsyncMock()
    player = LinkPlayPlayer(bridge)

    await player.resume()

    bridge.request.assert_called_once_with(LinkPlayCommand.RESUME)


async def test_player_mute():
    """Tests if the player mute is correctly called."""
    bridge = AsyncMock()
    player = LinkPlayPlayer(bridge)

    await player.mute()

    bridge.request.assert_called_once_with(LinkPlayCommand.MUTE)
    assert player.muted


async def test_player_unmute():
    """Tests if the player mute is correctly called."""
    bridge = AsyncMock()
    player = LinkPlayPlayer(bridge)
    player.properties[PlayerAttribute.MUTED] = MuteMode.MUTED

    await player.unmute()

    bridge.request.assert_called_once_with(LinkPlayCommand.UNMUTE)
    assert not player.muted


async def test_player_play_playlist():
    """Tests if the player play_playlist is correctly called."""
    bridge = AsyncMock()
    player = LinkPlayPlayer(bridge)

    await player.play_playlist(1)

    bridge.request.assert_called_once_with(LinkPlayCommand.PLAYLIST.format(1))


async def test_player_pause():
    """Tests if the player pause is correctly called."""
    bridge = AsyncMock()
    player = LinkPlayPlayer(bridge)

    await player.pause()

    bridge.request.assert_called_once_with(LinkPlayCommand.PAUSE)
    assert player.status == PlayingStatus.PAUSED


async def test_player_stop():
    """Tests if the player stop is correctly called."""
    bridge = AsyncMock()
    player = LinkPlayPlayer(bridge)

    await player.stop()

    bridge.request.assert_called_once_with(LinkPlayCommand.STOP)
    assert player.status == PlayingStatus.STOPPED


async def test_player_toggle():
    """Tests if the player pause is correctly called."""
    bridge = AsyncMock()
    player = LinkPlayPlayer(bridge)

    await player.toggle()

    bridge.request.assert_called_once_with(LinkPlayCommand.TOGGLE)


@pytest.mark.parametrize("volume", range(0, 101))
async def test_player_set_volume(volume: int):
    """Tests if the player set volume is correctly called."""
    bridge = AsyncMock()
    player = LinkPlayPlayer(bridge)

    await player.set_volume(volume)

    bridge.request.assert_called_once_with(LinkPlayCommand.VOLUME.format(volume))


@pytest.mark.parametrize("volume", [-1, 101])
async def test_player_set_volume_raises_value_error(volume: Any):
    """Tests if the player set volume is correctly called."""
    bridge = AsyncMock()
    player = LinkPlayPlayer(bridge)

    with pytest.raises(ValueError):
        await player.set_volume(volume)


async def test_player_invalid_playmode():
    """Tests if the player handles an invalid playmode correctly."""
    bridge = AsyncMock()
    player = LinkPlayPlayer(bridge)
    player.properties[PlayerAttribute.PLAYBACK_MODE] = 33

    assert player.play_mode == PlayingMode.IDLE


async def test_player_get_equalizer_mode_wiim():
    """Tests if the player handles an return the equalizer mode correctly."""
    bridge = AsyncMock()
    device = LinkPlayDevice(bridge)
    player = LinkPlayPlayer(bridge)
    bridge.device = device
    bridge.player = player
    bridge.device.properties[DeviceAttribute.PROJECT] = "WiiM_Pro_with_gc4a"

    player.properties[PlayerAttribute.EQUALIZER_MODE] = 0

    await player.set_equalizer_mode(EqualizerMode.JAZZ)

    player.properties[PlayerAttribute.EQUALIZER_MODE] = 0

    assert player.equalizer_mode == EqualizerMode.JAZZ


async def test_player_get_equalizer_mode():
    """Tests if the player handles an return the equalizer mode correctly."""
    bridge = AsyncMock()
    player = LinkPlayPlayer(bridge)
    player.properties[PlayerAttribute.EQUALIZER_MODE] = "1"

    assert player.equalizer_mode == EqualizerMode.CLASSIC


async def test_player_get_equalizer_mode_invalid():
    """Tests if the player handles an return the equalizer mode correctly."""
    bridge = AsyncMock()
    player = LinkPlayPlayer(bridge)
    player.properties[PlayerAttribute.EQUALIZER_MODE] = "invalid"

    assert player.equalizer_mode == EqualizerMode.NONE


async def test_player_set_equalizer_mode():
    """Tests if the player set equalizer mode is correctly called."""
    bridge = AsyncMock()
    player = LinkPlayPlayer(bridge)
    mode = EqualizerMode.JAZZ

    await player.set_equalizer_mode(mode)

    # Equalizer.Jazz is to be mapped to 3
    bridge.request.assert_called_once_with(LinkPlayCommand.EQUALIZER_MODE.format(3))


async def test_player_get_available_equalizer_modes():
    """Tests if the player get available equalizer modes is correctly called."""
    bridge = AsyncMock()
    player = LinkPlayPlayer(bridge)

    equalizer_modes = player.available_equalizer_modes

    assert equalizer_modes == [
        EqualizerMode.NONE,
        EqualizerMode.CLASSIC,
        EqualizerMode.POP,
        EqualizerMode.JAZZ,
        EqualizerMode.VOCAL,
    ]


async def test_player_set_loop_mode():
    """Tests if the player set loop mode is correctly called."""
    bridge = AsyncMock()
    player = LinkPlayPlayer(bridge)
    mode = LoopMode.CONTINUOUS_PLAYBACK

    await player.set_loop_mode(mode)

    bridge.request.assert_called_once_with(LinkPlayCommand.LOOP_MODE.format(mode))


async def test_player_set_play_mode():
    """Tests if the player set play mode is correctly called."""
    bridge = AsyncMock()
    player = LinkPlayPlayer(bridge)
    mode = PlayingMode.NETWORK
    mode_conv = PLAY_MODE_SEND_MAP[mode]

    await player.set_play_mode(mode)

    bridge.request.assert_called_once_with(
        LinkPlayCommand.SWITCH_MODE.format(mode_conv)
    )


@pytest.mark.parametrize("preset_number", range(1, 11))
async def test_player_play_preset_when_max_key_empty(preset_number: int):
    """Tests if a player is able to play a preset."""
    bridge = AsyncMock()
    device = LinkPlayDevice(bridge)
    player = LinkPlayPlayer(bridge)
    bridge.device = device
    bridge.player = player

    bridge.device.properties[DeviceAttribute.PRESET_KEY] = ""

    await player.play_preset(preset_number)

    bridge.request.assert_called_once_with(
        LinkPlayCommand.PLAY_PRESET.format(preset_number)
    )


@pytest.mark.parametrize("preset_number", range(1, 11))
async def test_player_play_preset(preset_number: int):
    """Tests if a player is able to play a preset."""
    bridge = AsyncMock()
    device = LinkPlayDevice(bridge)
    player = LinkPlayPlayer(bridge)
    bridge.device = device
    bridge.player = player

    await player.play_preset(preset_number)

    bridge.request.assert_called_once_with(
        LinkPlayCommand.PLAY_PRESET.format(preset_number)
    )


@pytest.mark.parametrize(
    "preset_number",
    [
        0,
        11,
    ],
)
async def test_player_play_preset_raises_value_error(preset_number: int):
    """Tests that a player fails in an expected way if play preset input is incorrect."""
    bridge = AsyncMock()
    device = LinkPlayDevice(bridge)
    player = LinkPlayPlayer(bridge)
    bridge.device = device
    bridge.player = player

    with pytest.raises(ValueError):
        await player.play_preset(preset_number)


async def test_deserialize_player():
    """Test the player to deserialize correctly."""
    bridge = AsyncMock()
    player = LinkPlayPlayer(bridge)

    player.to_dict()


async def test_multiroom_setup():
    """Tests if multiroom sets up correctly."""
    leader = AsyncMock()

    multiroom = LinkPlayMultiroom(leader)

    assert multiroom.leader == leader
    assert not multiroom.followers


async def test_multiroom_update_status():
    """Tests if MultiRoom update status works correctly."""
    leader = AsyncMock()
    bridges = [leader, AsyncMock()]
    multiroom = LinkPlayMultiroom(leader)

    await multiroom.update_status(bridges)

    leader.json_request.assert_called_once_with(LinkPlayCommand.MULTIROOM_LIST)
    assert multiroom.leader == leader


async def test_multiroom_ungroup():
    """Tests if multiroom ungroup is correctly called on the leader."""
    leader = AsyncMock()
    multiroom = LinkPlayMultiroom(leader)
    multiroom.followers = [AsyncMock()]

    await multiroom.ungroup()

    leader.request.assert_called_once_with(LinkPlayCommand.MULTIROOM_UNGROUP)
    assert not multiroom.followers


async def test_multiroom_add_follower():
    """Tests if multiroom add follower is correctly called on the follower."""
    leader = AsyncMock()
    leader.device.eth = "1.2.3.4"
    follower = AsyncMock()
    multiroom = LinkPlayMultiroom(leader)

    await multiroom.add_follower(follower)

    follower.request.assert_called_once_with(
        LinkPlayCommand.MULTIROOM_JOIN.format(leader.device.eth)
    )
    assert multiroom.followers == [follower]


async def test_multiroom_remove_follower():
    """Tests if multiroom remove folllower is correctly called on the leader."""
    leader = AsyncMock()
    follower = AsyncMock()
    follower.device.eth = "1.2.3.4"
    multiroom = LinkPlayMultiroom(leader)
    multiroom.followers = [follower]

    await multiroom.remove_follower(follower)

    leader.request.assert_called_once_with(
        LinkPlayCommand.MULTIROOM_KICK.format(follower.device.eth)
    )
    assert not multiroom.followers


async def test_multiroom_mute():
    """Tests if multiroom mute is correctly called on the leader."""
    leader = AsyncMock()
    multiroom = LinkPlayMultiroom(leader)

    await multiroom.mute()

    leader.request.assert_called_once_with(LinkPlayCommand.MULTIROOM_MUTE)


async def test_multiroom_unmute():
    """Tests if multiroom unmute is correctly called on the leader."""
    leader = AsyncMock()
    multiroom = LinkPlayMultiroom(leader)

    await multiroom.unmute()

    leader.request.assert_called_once_with(LinkPlayCommand.MULTIROOM_UNMUTE)


@pytest.mark.parametrize("volume", range(0, 101))
async def test_multiroom_set_volume(volume: int):
    """Tests if multiroom set volume is correctly called on the leader."""
    leader = AsyncMock()
    multiroom = LinkPlayMultiroom(leader)

    await multiroom.set_volume(volume)

    leader.request.assert_called_once_with(LinkPlayCommand.MULTIROOM_VOL.format(volume))


@pytest.mark.parametrize("volume", [-1, 101])
async def test_multiroom_set_volume_raises_value_error(volume: int):
    """Tests if multiroom set volume is correctly called on the leader."""
    leader = AsyncMock()
    multiroom = LinkPlayMultiroom(leader)

    with pytest.raises(ValueError):
        await multiroom.set_volume(volume)


@pytest.fixture
def mock_bridge():
    bridge = Mock(spec=LinkPlayBridge)
    bridge.device = Mock(spec=LinkPlayDevice)
    return bridge


def test_set_callback_assigns_controller(mock_bridge):
    """Test that set_callback assigns the controller correctly."""
    device = LinkPlayDevice(mock_bridge)
    mock_controller = Mock()

    device.set_callback(mock_controller)

    assert device.controller == mock_controller


@pytest.mark.asyncio
async def test_update_status_triggers_controller_on_mode_change_to_follower(
    mock_bridge,
):
    """Test that update_status triggers the controller when playing mode changes to FOLLOWER."""
    player = LinkPlayPlayer(mock_bridge)
    mock_bridge.device.controller = Mock()

    # Simulate initial state
    player.previous_playing_mode = PlayingMode.IDLE
    mock_bridge.json_request = AsyncMock(
        return_value={PlayerAttribute.PLAYBACK_MODE: PlayingMode.FOLLOWER}
    )

    # Call update_status and verify controller is called
    await player.update_status()

    mock_bridge.device.controller.assert_called_once()


@pytest.mark.asyncio
async def test_update_status_triggers_controller_on_mode_change_from_follower(
    mock_bridge,
):
    """Test that update_status triggers the controller when playing mode changes from FOLLOWER."""
    player = LinkPlayPlayer(mock_bridge)
    mock_bridge.device.controller = Mock()

    # Simulate initial state
    player.previous_playing_mode = PlayingMode.FOLLOWER
    mock_bridge.json_request = AsyncMock(
        return_value={PlayerAttribute.PLAYBACK_MODE: PlayingMode.IDLE}
    )

    # Call update_status and verify controller is called
    await player.update_status()

    mock_bridge.device.controller.assert_called_once()


@pytest.mark.asyncio
async def test_update_status_does_not_trigger_controller_on_no_mode_change(mock_bridge):
    """Test that update_status does not trigger the controller when playing mode remains FOLLOWER."""
    player = LinkPlayPlayer(mock_bridge)
    mock_bridge.device.controller = Mock()

    # Simulate no change in playing mode
    player.previous_playing_mode = PlayingMode.FOLLOWER
    mock_bridge.json_request = AsyncMock(
        return_value={PlayerAttribute.PLAYBACK_MODE: PlayingMode.FOLLOWER}
    )

    await player.update_status()

    mock_bridge.device.controller.assert_not_called()

    player.previous_playing_mode = PlayingMode.IDLE
    mock_bridge.json_request = AsyncMock(
        return_value={PlayerAttribute.PLAYBACK_MODE: PlayingMode.IDLE}
    )

    await player.update_status()

    mock_bridge.device.controller.assert_not_called()


async def test_meta_info_failed_handling():
    """Test that the player handles a failed META_INFO request correctly."""

    async def mock_session_call_api_json_side_effect(endpoint, session, command):
        if command == LinkPlayCommand.META_INFO:
            return "Failed"
        return "{}"

    # Mock the session_call_api function
    with patch(
        "linkplay.utils.session_call_api",
        new=AsyncMock(side_effect=mock_session_call_api_json_side_effect),
    ) as mock_api:
        # Mock the bridge and its device
        mock_bridge = LinkPlayBridge(
            endpoint=LinkPlayApiEndpoint(
                protocol="http", port=80, endpoint="1.2.3.4", session=None
            )
        )
        mock_bridge.device = MagicMock()
        mock_bridge.device.manufacturer = (
            MANUFACTURER_WIIM  # Set the manufacturer to WiiM
        )

        # Create a LinkPlayPlayer instance with the mocked bridge
        player = LinkPlayPlayer(mock_bridge)

        # Simulate the META_INFO request and exception handling
        await player.update_status()

        # Verify that metainfo is set to an empty dictionary after the exception
        assert player.metainfo == {}

        # Verify that the mocked function was called with the correct command
        mock_api.assert_called_with("http://1.2.3.4", None, LinkPlayCommand.META_INFO)


async def test_audio_output_control():
    """Test that the player handles a audio output control correctly."""

    async def mock_session_call_api_json_side_effect(endpoint, session, command):
        if command == LinkPlayCommand.AUDIO_OUTPUT_HW_MODE:
            return """{"hardware":"2","source":"0","audiocast":"0"}"""
        return "{}"

    # Mock the session_call_api function
    with patch(
        "linkplay.utils.session_call_api",
        new=AsyncMock(side_effect=mock_session_call_api_json_side_effect),
    ) as mock_api:
        # Mock the bridge and its device
        mock_bridge = LinkPlayBridge(
            endpoint=LinkPlayApiEndpoint(
                protocol="http", port=80, endpoint="1.2.3.4", session=None
            )
        )
        mock_bridge.device = MagicMock()
        mock_bridge.device.manufacturer = (
            MANUFACTURER_WIIM  # Set the manufacturer to WiiM
        )

        # Create a LinkPlayPlayer instance with the mocked bridge
        player = LinkPlayPlayer(mock_bridge)

        # Simulate the META_INFO request and exception handling
        resp = await player.get_audio_output_mode()

        # Verify that metainfo is set to an empty dictionary after the exception
        assert resp.hardware == AudioOutputHwMode.LINE_OUT
        assert not resp.bluetooth_source
        assert not resp.audiocast

        # Verify that the mocked function was called with the correct command
        mock_api.assert_called_with(
            "http://1.2.3.4", None, LinkPlayCommand.AUDIO_OUTPUT_HW_MODE
        )
