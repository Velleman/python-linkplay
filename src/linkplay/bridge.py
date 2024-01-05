from typing import Dict

from aiohttp import ClientSession

from linkplay.consts import LinkPlayCommand, DeviceAttribute, PlayerAttribute, MuteMode, EqualizerMode, LoopMode, PlaybackMode, PLAYBACK_MODE_MAP, PlaymodeSupport
from linkplay.utils import session_call_api_json, session_call_api_ok, decode_hexstr


class LinkPlayBridge():
    """Represents a LinkPlay device."""

    protocol: str
    ip_address: str
    device_status: Dict[DeviceAttribute, str] = dict.fromkeys(DeviceAttribute.__members__.values(), "")
    player_status: Dict[PlayerAttribute, str] = dict.fromkeys(PlayerAttribute.__members__.values(), "")

    def __init__(self, protocol: str, ip_address: str):
        self.protocol = protocol
        self.ip_address = ip_address

    def __repr__(self) -> str:
        if self.device_status[DeviceAttribute.DEVICE_NAME] == "":
            return self.endpoint

        return self.device_status[DeviceAttribute.DEVICE_NAME]

    async def update_device_status(self, session: ClientSession) -> None:
        """Update the device status."""
        self.device_status = await session_call_api_json(self.endpoint, session, LinkPlayCommand.DEVICE_STATUS)  # type: ignore[assignment]

    async def update_player_status(self, session: ClientSession):
        """Update the player status."""
        self.player_status = await session_call_api_json(self.endpoint, session, LinkPlayCommand.PLAYER_STATUS)  # type: ignore[assignment]
        self.player_status[PlayerAttribute.TITLE] = decode_hexstr(self.title)
        self.player_status[PlayerAttribute.ARTIST] = decode_hexstr(self.artist)
        self.player_status[PlayerAttribute.ALBUM] = decode_hexstr(self.album)

    async def next(self, session: ClientSession):
        """Play the next song in the playlist."""
        await session_call_api_ok(self.endpoint, session, LinkPlayCommand.NEXT)

    async def previous(self, session: ClientSession):
        """Play the previous song in the playlist."""
        await session_call_api_ok(self.endpoint, session, LinkPlayCommand.PREVIOUS)

    async def play(self, session: ClientSession, value: str):
        """Start playing the selected track."""
        await session_call_api_ok(self.endpoint, session, LinkPlayCommand.PLAY.format(value))  # type: ignore[str-format]

    async def resume(self, session: ClientSession):
        """Resume playing the current track."""
        await session_call_api_ok(self.endpoint, session, LinkPlayCommand.RESUME)

    async def mute(self, session: ClientSession):
        """Mute the player."""
        await session_call_api_ok(self.endpoint, session, LinkPlayCommand.MUTE)
        self.player_status[PlayerAttribute.MUTED] = MuteMode.MUTED

    async def unmute(self, session: ClientSession):
        """Unmute the player."""
        await session_call_api_ok(self.endpoint, session, LinkPlayCommand.UNMUTE)
        self.player_status[PlayerAttribute.MUTED] = MuteMode.UNMUTED

    async def play_playlist(self, session: ClientSession, index: int):
        """Start playing chosen playlist by index number."""
        await session_call_api_ok(self.endpoint, session, LinkPlayCommand.PLAYLIST.format(index))  # type: ignore[str-format]

    async def pause(self, session: ClientSession):
        """Pause the current playing track."""
        await session_call_api_ok(self.endpoint, session, LinkPlayCommand.PAUSE)

    async def toggle(self, session: ClientSession):
        """Start playing if the player is currently not playing. Stops playing if it is."""
        await session_call_api_ok(self.endpoint, session, LinkPlayCommand.TOGGLE)

    async def set_volume(self, session: ClientSession, value: int):
        """Set the player volume."""
        if not 0 <= value <= 100:
            raise ValueError("Volume must be between 0 and 100.")

        await session_call_api_ok(self.endpoint, session, LinkPlayCommand.VOLUME.format(value))  # type: ignore[str-format]
        self.player_status[PlayerAttribute.VOLUME] = str(value)

    async def set_equalizer_mode(self, session: ClientSession, mode: EqualizerMode):
        """Set the equalizer mode."""
        await session_call_api_ok(self.endpoint, session, LinkPlayCommand.EQUALIZER_MODE.format(mode))  # type: ignore[str-format]

    async def set_loop_mode(self, session: ClientSession, mode: LoopMode):
        """Set the loop mode."""
        await session_call_api_ok(self.endpoint, session, LinkPlayCommand.LOOP_MODE.format(mode))  # type: ignore[str-format]

    async def set_play_mode(self, session: ClientSession, mode: PlaybackMode):
        """Set the play mode."""
        await session_call_api_ok(self.endpoint, session, LinkPlayCommand.SWITCH_MODE.format(PLAYBACK_MODE_MAP[mode]))  # type: ignore[str-format]

    async def reboot(self, session: ClientSession):
        """Reboot the player."""
        await session_call_api_ok(self.endpoint, session, LinkPlayCommand.REBOOT)

    @property
    def endpoint(self) -> str:
        """Returns the current player endpoint."""
        return f"{self.protocol}://{self.ip_address}"

    @property
    def muted(self) -> bool:
        """Returns if the player is muted."""
        return self.player_status[PlayerAttribute.MUTED] == MuteMode.MUTED

    @property
    def title(self) -> str:
        """Returns if the currently playing title of the track."""
        return self.player_status[PlayerAttribute.TITLE]

    @property
    def artist(self) -> str:
        """Returns if the currently playing artist."""
        return self.player_status[PlayerAttribute.ARTIST]

    @property
    def album(self) -> str:
        """Returns if the currently playing album."""
        return self.player_status[PlayerAttribute.ALBUM]

    @property
    def volume(self) -> int:
        """Returns the player volume, expressed in %."""
        return int(self.player_status[PlayerAttribute.VOLUME])

    @property
    def playmode_support(self) -> PlaymodeSupport:
        """Returns the player playmode support."""
        return PlaymodeSupport(int(self.device_status[DeviceAttribute.PLAYMODE_SUPPORT], base=16))
