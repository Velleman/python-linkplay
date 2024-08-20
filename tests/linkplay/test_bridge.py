"""Test bridge functionality."""

from unittest.mock import AsyncMock

from linkplay.bridge import (
    LinkPlayBridge,
    LinkPlayDevice,
    LinkPlayMultiroom,
    LinkPlayPlayer,
)
from linkplay.consts import (
    PLAY_MODE_SEND_MAP,
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


def test_device_name():
    """Tests if the device name is correctly set up."""
    endpoint: LinkPlayApiEndpoint = LinkPlayApiEndpoint(
        protocol="http", endpoint="1.2.3.4", session=None
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


async def test_player_update_status():
    """Tests if the player update status is correctly called."""
    bridge = AsyncMock()
    bridge.json_request.return_value = {
        PlayerAttribute.TITLE: "556E6B6E6F776E",
        PlayerAttribute.ARTIST: "556E6B6E6F776E",
        PlayerAttribute.ALBUM: "556E6B6E6F776E",
    }
    player = LinkPlayPlayer(bridge)

    await player.update_status()

    bridge.json_request.assert_called_once_with(LinkPlayCommand.PLAYER_STATUS)
    assert player.title == "Unknown"


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


async def test_player_toggle():
    """Tests if the player pause is correctly called."""
    bridge = AsyncMock()
    player = LinkPlayPlayer(bridge)

    await player.toggle()

    bridge.request.assert_called_once_with(LinkPlayCommand.TOGGLE)


async def test_player_set_volume():
    """Tests if the player set volume is correctly called."""
    bridge = AsyncMock()
    player = LinkPlayPlayer(bridge)

    await player.set_volume(100)

    bridge.request.assert_called_once_with(LinkPlayCommand.VOLUME.format(100))


async def test_player_set_equalizer_mode():
    """Tests if the player set equalizer mode is correctly called."""
    bridge = AsyncMock()
    player = LinkPlayPlayer(bridge)
    mode = EqualizerMode.JAZZ

    await player.set_equalizer_mode(mode)

    bridge.request.assert_called_once_with(LinkPlayCommand.EQUALIZER_MODE.format(mode))


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


async def test_multiroom_set_volume():
    """Tests if multiroom set volume is correctly called on the leader."""
    leader = AsyncMock()
    multiroom = LinkPlayMultiroom(leader)

    await multiroom.set_volume(100)

    leader.request.assert_called_once_with(LinkPlayCommand.MULTIROOM_VOL.format(100))
