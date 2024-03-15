from __future__ import annotations

from aiohttp import ClientSession

from linkplay.consts import (
    ChannelType,
    LinkPlayCommand,
    DeviceAttribute,
    PlayerAttribute,
    MuteMode,
    EqualizerMode,
    LoopMode,
    PLAY_MODE_SEND_MAP,
    PlayingStatus,
    InputMode,
    SpeakerType,
    PlayingMode,
    INPUT_MODE_MAP
)
from linkplay.utils import session_call_api_json, session_call_api_ok, decode_hexstr


class LinkPlayDevice():
    """Represents a LinkPlay device."""

    bridge: LinkPlayBridge
    properties: dict[DeviceAttribute, str] = dict.fromkeys(DeviceAttribute.__members__.values(), "")

    def __init__(self, bridge: LinkPlayBridge):
        self.bridge = bridge

    async def update_status(self) -> None:
        """Update the device status."""
        self.properties = await self.bridge.json_request(LinkPlayCommand.DEVICE_STATUS)  # type: ignore[assignment]

    async def reboot(self):
        """Reboot the device."""
        await self.bridge.request(LinkPlayCommand.REBOOT)

    @property
    def uuid(self) -> str:
        """The UUID of the device."""
        return self.properties[DeviceAttribute.UUID]

    @property
    def name(self) -> str:
        """The name of the device."""
        return self.properties[DeviceAttribute.DEVICE_NAME]

    @property
    def playmode_support(self) -> list[PlayingMode]:
        """Returns the player playmode support."""

        flags = InputMode(int(self.properties[DeviceAttribute.PLAYMODE_SUPPORT], base=16))
        return [INPUT_MODE_MAP[flag] for flag in flags]

    @property
    def eth(self) -> str:
        """Returns the ethernet address."""
        return self.properties[DeviceAttribute.ETH_DHCP]


class LinkPlayPlayer():
    """Represents a LinkPlay player."""

    bridge: LinkPlayBridge
    properties: dict[PlayerAttribute, str] = dict.fromkeys(PlayerAttribute.__members__.values(), "")

    def __init__(self, bridge: LinkPlayBridge):
        self.bridge = bridge

    async def update_status(self):
        """Update the player status."""
        self.properties = await self.bridge.json_request(LinkPlayCommand.PLAYER_STATUS)  # type: ignore[assignment]
        self.properties[PlayerAttribute.TITLE] = decode_hexstr(self.title)
        self.properties[PlayerAttribute.ARTIST] = decode_hexstr(self.artist)
        self.properties[PlayerAttribute.ALBUM] = decode_hexstr(self.album)

    async def next(self):
        """Play the next song in the playlist."""
        await self.bridge.request(LinkPlayCommand.NEXT)

    async def previous(self):
        """Play the previous song in the playlist."""
        await self.bridge.request(LinkPlayCommand.PREVIOUS)

    async def play(self, value: str):
        """Start playing the selected track."""
        await self.bridge.request(LinkPlayCommand.PLAY.format(value))  # type: ignore[str-format]

    async def resume(self):
        """Resume playing the current track."""
        await self.bridge.request(LinkPlayCommand.RESUME)

    async def mute(self):
        """Mute the player."""
        await self.bridge.request(LinkPlayCommand.MUTE)
        self.properties[PlayerAttribute.MUTED] = MuteMode.MUTED

    async def unmute(self):
        """Unmute the player."""
        await self.bridge.request(LinkPlayCommand.UNMUTE)
        self.properties[PlayerAttribute.MUTED] = MuteMode.UNMUTED

    async def play_playlist(self, index: int):
        """Start playing chosen playlist by index number."""
        await self.bridge.request(LinkPlayCommand.PLAYLIST.format(index))  # type: ignore[str-format]

    async def pause(self):
        """Pause the current playing track."""
        await self.bridge.request(LinkPlayCommand.PAUSE)
        self.properties[PlayerAttribute.PLAYING_STATUS] = PlayingStatus.PAUSED

    async def toggle(self):
        """Start playing if the player is currently not playing. Stops playing if it is."""
        await self.bridge.request(LinkPlayCommand.TOGGLE)

    async def set_volume(self, value: int):
        """Set the player volume."""
        if not 0 <= value <= 100:
            raise ValueError("Volume must be between 0 and 100.")

        await self.bridge.request(LinkPlayCommand.VOLUME.format(value))  # type: ignore[str-format]

    async def set_equalizer_mode(self, mode: EqualizerMode):
        """Set the equalizer mode."""
        await self.bridge.request(LinkPlayCommand.EQUALIZER_MODE.format(mode))  # type: ignore[str-format]

    async def set_loop_mode(self, mode: LoopMode):
        """Set the loop mode."""
        await self.bridge.request(LinkPlayCommand.LOOP_MODE.format(mode))  # type: ignore[str-format]

    async def set_play_mode(self, mode: PlayingMode):
        """Set the play mode."""
        await self.bridge.request(LinkPlayCommand.SWITCH_MODE.format(PLAY_MODE_SEND_MAP[mode]))  # type: ignore[str-format]

    @property
    def muted(self) -> bool:
        """Returns if the player is muted."""
        return self.properties[PlayerAttribute.MUTED] == MuteMode.MUTED

    @property
    def title(self) -> str:
        """Returns if the currently playing title of the track."""
        return self.properties[PlayerAttribute.TITLE]

    @property
    def artist(self) -> str:
        """Returns if the currently playing artist."""
        return self.properties[PlayerAttribute.ARTIST]

    @property
    def album(self) -> str:
        """Returns if the currently playing album."""
        return self.properties[PlayerAttribute.ALBUM]

    @property
    def volume(self) -> int:
        """Returns the player volume, expressed in %."""
        return int(self.properties[PlayerAttribute.VOLUME])

    @property
    def current_position(self) -> int:
        """Returns the current position of the track in milliseconds."""
        return int(self.properties[PlayerAttribute.CURRENT_POSITION])

    @property
    def total_length(self) -> int:
        """Returns the total length of the track in milliseconds."""
        return int(self.properties[PlayerAttribute.TOTAL_LENGTH])

    @property
    def status(self) -> PlayingStatus:
        """Returns the current playing status."""
        return PlayingStatus(self.properties[PlayerAttribute.PLAYING_STATUS])

    @property
    def equalizer_mode(self) -> EqualizerMode:
        """Returns the current equalizer mode."""
        return EqualizerMode(self.properties[PlayerAttribute.EQUALIZER_MODE])

    @property
    def speaker_type(self) -> SpeakerType:
        """Returns the current speaker the player is playing on."""
        return SpeakerType(self.properties[PlayerAttribute.SPEAKER_TYPE])

    @property
    def channel_type(self) -> ChannelType:
        """Returns the channel the player is playing on."""
        return ChannelType(self.properties[PlayerAttribute.CHANNEL_TYPE])

    @property
    def play_mode(self) -> PlayingMode:
        """Returns the current playing mode of the player."""
        return PlayingMode(self.properties[PlayerAttribute.PLAYBACK_MODE])

    @property
    def loop_mode(self) -> LoopMode:
        """Returns the current playlist mode."""
        return LoopMode(self.properties[PlayerAttribute.PLAYLIST_MODE])


class LinkPlayBridge():
    """Represents a LinkPlay bridge to control the device and player attached to it."""

    protocol: str
    ip_address: str
    session: ClientSession
    device: LinkPlayDevice
    player: LinkPlayPlayer

    def __init__(self, protocol: str, ip_address: str, session: ClientSession):
        self.protocol = protocol
        self.ip_address = ip_address
        self.session = session
        self.device = LinkPlayDevice(self)
        self.player = LinkPlayPlayer(self)

    def __repr__(self) -> str:
        if self.device.name == "":
            return self.endpoint

        return self.device.name

    @property
    def endpoint(self) -> str:
        """Returns the current player endpoint."""
        return f"{self.protocol}://{self.ip_address}"

    async def json_request(self, command: str) -> dict[str, str]:
        """Performs a GET request on the given command and returns the result as a JSON object."""
        return await session_call_api_json(self.endpoint, self.session, command)

    async def request(self, command: str) -> None:
        """Performs a GET request on the given command and verifies the result."""
        await session_call_api_ok(self.endpoint, self.session, command)


class LinkPlayMultiroom():
    """Represents a LinkPlay multiroom group. Contains a leader and a list of followers.
    The leader is the device that controls the group."""

    leader: LinkPlayBridge
    followers: list[LinkPlayBridge]

    def __init__(self, leader: LinkPlayBridge, followers: list[LinkPlayBridge]):
        self.leader = leader
        self.followers = followers

    async def ungroup(self):
        """Ungroups the multiroom group."""
        await self.leader.request(LinkPlayCommand.MULTIROOM_UNGROUP)
        self.followers = []

    async def add_follower(self, follower: LinkPlayBridge):
        """Adds a follower to the multiroom group."""
        await follower.request(LinkPlayCommand.MULTIROOM_JOIN.format(self.leader.device.eth))  # type: ignore[str-format]
        self.followers.append(follower)

    async def remove_follower(self, follower: LinkPlayBridge):
        """Removes a follower from the multiroom group."""
        await self.leader.request(LinkPlayCommand.MULTIROOM_KICK.format(follower.device.eth))  # type: ignore[str-format]
        self.followers.remove(follower)

    async def set_volume(self, value: int):
        """Sets the volume for the multiroom group."""
        assert 0 < value <= 100
        str_vol = str(value)
        await self.leader.request(LinkPlayCommand.MULTIROOM_VOL.format(str_vol))  # type: ignore[str-format]

        for bridge in [self.leader] + self.followers:
            bridge.player.properties[PlayerAttribute.VOLUME] = str_vol

    async def mute(self):
        """Mutes the multiroom group."""
        await self.leader.request(LinkPlayCommand.MULTIROOM_MUTE)

    async def unmute(self):
        """Unmutes the multiroom group."""
        await self.leader.request(LinkPlayCommand.MULTIROOM_UNMUTE)
