from __future__ import annotations
from typing import Dict

from aiohttp import ClientSession

from linkplay.consts import (
    LinkPlayCommand,
    DeviceAttribute,
    PlayerAttribute,
    MuteMode,
    EqualizerMode,
    LoopMode,
    PlaybackMode,
    PLAYBACK_MODE_MAP,
    PlaymodeSupport
)
from linkplay.utils import session_call_api_json, session_call_api_ok, decode_hexstr


class LinkPlayDevice():
    """Represents a LinkPlay device."""

    bridge: LinkPlayBridge
    properties: Dict[DeviceAttribute, str] = dict.fromkeys(DeviceAttribute.__members__.values(), "")

    def __init__(self, bridge: LinkPlayBridge):
        self.bridge = bridge

    async def update_status(self) -> None:
        """Update the device status."""
        self.properties = await self.bridge.json_request(LinkPlayCommand.DEVICE_STATUS)  # type: ignore[assignment]

    async def reboot(self):
        """Reboot the device."""
        await self.bridge.request(LinkPlayCommand.REBOOT)

    @property
    def name(self) -> str:
        """The name of the device."""
        return self.properties[DeviceAttribute.DEVICE_NAME]

    @property
    def playmode_support(self) -> PlaymodeSupport:
        """Returns the player playmode support."""
        return PlaymodeSupport(int(self.properties[DeviceAttribute.PLAYMODE_SUPPORT], base=16))


class LinkPlayPlayer():
    """Represents a LinkPlay player."""

    bridge: LinkPlayBridge
    properties: Dict[PlayerAttribute, str] = dict.fromkeys(PlayerAttribute.__members__.values(), "")

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

    async def toggle(self):
        """Start playing if the player is currently not playing. Stops playing if it is."""
        await self.bridge.request(LinkPlayCommand.TOGGLE)

    async def set_volume(self, value: int):
        """Set the player volume."""
        if not 0 <= value <= 100:
            raise ValueError("Volume must be between 0 and 100.")

        await self.bridge.request(LinkPlayCommand.VOLUME.format(value))  # type: ignore[str-format]
        self.properties[PlayerAttribute.VOLUME] = str(value)

    async def set_equalizer_mode(self, mode: EqualizerMode):
        """Set the equalizer mode."""
        await self.bridge.request(LinkPlayCommand.EQUALIZER_MODE.format(mode))  # type: ignore[str-format]

    async def set_loop_mode(self, mode: LoopMode):
        """Set the loop mode."""
        await self.bridge.request(LinkPlayCommand.LOOP_MODE.format(mode))  # type: ignore[str-format]

    async def set_play_mode(self, mode: PlaybackMode):
        """Set the play mode."""
        await self.bridge.request(LinkPlayCommand.SWITCH_MODE.format(PLAYBACK_MODE_MAP[mode]))  # type: ignore[str-format]

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


class LinkPlayBridge():
    """Represents a LinkPlay device."""

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

    async def json_request(self, command: str) -> Dict[str, str]:
        """Performs a GET request on the given command and returns the result as a JSON object."""
        return await session_call_api_json(self.endpoint, self.session, command)

    async def request(self, command: str) -> None:
        """Performs a GET request on the given command and verifies the result."""
        await session_call_api_ok(self.endpoint, self.session, command)
