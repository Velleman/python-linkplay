from typing import Dict
from aiohttp import ClientSession

from linkplay.consts import LinkPlayCommand, DeviceStatus, PlayerStatus, MuteMode, UNKNOWN_TRACK_PLAYING
from linkplay.utils import session_call_api_json, session_call_api_ok


class LinkPlayBridge():
    """Represents a LinkPlay device."""

    protocol: str
    ip: str
    device_status: Dict[DeviceStatus, str] = dict.fromkeys(DeviceStatus.__members__.values(), None)
    player_status: Dict[PlayerStatus, str] = dict.fromkeys(PlayerStatus.__members__.values(), None)

    def __init__(self, protocol: str, ip: str):
        self.protocol = protocol
        self.ip = ip

    def __repr__(self) -> str:
        if not self.device_status[DeviceStatus.DEVICE_NAME]:
            return self.endpoint

        return self.device_status[DeviceStatus.DEVICE_NAME]

    async def update_device_status(self, session: ClientSession) -> None:
        """Update the device status."""
        self.device_status = await session_call_api_json(self.endpoint, session, LinkPlayCommand.DEVICE_STATUS)

    async def update_player_status(self, session: ClientSession):
        """Update the player status."""
        self.player_status = await session_call_api_json(self.endpoint, session, LinkPlayCommand.PLAYER_STATUS)
        self.player_status[PlayerStatus.TITLE] = bytes.fromhex(self.player_status[PlayerStatus.TITLE]).decode("utf-8")
        self.player_status[PlayerStatus.ARTIST] = bytes.fromhex(self.player_status[PlayerStatus.ARTIST]).decode("utf-8")
        self.player_status[PlayerStatus.ALBUM] = bytes.fromhex(self.player_status[PlayerStatus.ALBUM]).decode("utf-8")

        if self.title == UNKNOWN_TRACK_PLAYING and self.artist == UNKNOWN_TRACK_PLAYING and self.album == UNKNOWN_TRACK_PLAYING:
            self.player_status[PlayerStatus.TITLE], self.player_status[PlayerStatus.ARTIST], self.player_status[PlayerStatus.ALBUM] = None, None, None

    async def next(self, session: ClientSession):
        """Play the next song in the playlist."""
        await session_call_api_ok(self.endpoint, session, LinkPlayCommand.NEXT)

    async def previous(self, session: ClientSession):
        """Play the previous song in the playlist."""
        await session_call_api_ok(self.endpoint, session, LinkPlayCommand.PREVIOUS)

    async def play(self, session: ClientSession, value: str):
        """Start playing the selected track."""
        await session_call_api_ok(self.endpoint, session, LinkPlayCommand.PLAY.format(value))

    async def resume(self, session: ClientSession):
        """Resume playing the current track."""
        await session_call_api_ok(self.endpoint, session, LinkPlayCommand.RESUME)

    async def mute(self, session: ClientSession):
        """Mute the player."""
        await session_call_api_ok(self.endpoint, session, LinkPlayCommand.MUTE)
        self.player_status[PlayerStatus.MUTED] = MuteMode.MUTED

    async def unmute(self, session: ClientSession):
        """Unmute the player."""
        await session_call_api_ok(self.endpoint, session, LinkPlayCommand.UNMUTE)
        self.player_status[PlayerStatus.MUTED] = MuteMode.UNMUTED

    async def play_playlist(self, session: ClientSession, index: int):
        """Start playing chosen playlist by index number."""
        await session_call_api_ok(self.endpoint, session, LinkPlayCommand.PLAYLIST.format(index))

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

        await session_call_api_ok(self.endpoint, session, LinkPlayCommand.VOLUME.format(value))
        self.player_status[PlayerStatus.VOLUME] = str(value)

    @property
    def endpoint(self) -> str:
        """Returns the current player endpoint."""
        return f"{self.protocol}://{self.ip}"

    @property
    def muted(self) -> bool:
        """Returns if the player is muted."""
        return self.player_status[PlayerStatus.MUTED] == MuteMode.MUTED

    @property
    def title(self) -> str:
        """Returns if the currently playing title of the track."""
        return self.player_status[PlayerStatus.TITLE]

    @property
    def artist(self) -> str:
        """Returns if the currently playing artist."""
        return self.player_status[PlayerStatus.ARTIST]

    @property
    def album(self) -> str:
        """Returns if the currently playing album."""
        return self.player_status[PlayerStatus.ALBUM]

    @property
    def volume(self) -> int:
        """Returns the player volume."""
        return int(self.player_status[PlayerStatus.VOLUME])
