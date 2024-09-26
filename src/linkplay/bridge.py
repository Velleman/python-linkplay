from __future__ import annotations

from typing import Any

from linkplay.consts import (
    INPUT_MODE_MAP,
    PLAY_MODE_SEND_MAP,
    ChannelType,
    DeviceAttribute,
    EqualizerMode,
    InputMode,
    LinkPlayCommand,
    LoopMode,
    MultiroomAttribute,
    MuteMode,
    PlayerAttribute,
    PlayingMode,
    PlayingStatus,
    SpeakerType,
)
from linkplay.endpoint import LinkPlayEndpoint
from linkplay.utils import fixup_player_properties


class LinkPlayDevice:
    """Represents a LinkPlay device."""

    bridge: LinkPlayBridge
    properties: dict[DeviceAttribute, str] = dict.fromkeys(
        DeviceAttribute.__members__.values(), ""
    )

    def __init__(self, bridge: LinkPlayBridge):
        self.bridge = bridge

    async def update_status(self) -> None:
        """Update the device status."""
        self.properties = await self.bridge.json_request(LinkPlayCommand.DEVICE_STATUS)  # type: ignore[assignment]

    async def reboot(self) -> None:
        """Reboot the device."""
        await self.bridge.request(LinkPlayCommand.REBOOT)

    @property
    def uuid(self) -> str:
        """The UUID of the device."""
        return self.properties.get(DeviceAttribute.UUID, "")

    @property
    def name(self) -> str:
        """The name of the device."""
        return self.properties.get(DeviceAttribute.DEVICE_NAME, "")

    @property
    def playmode_support(self) -> list[PlayingMode]:
        """Returns the player playmode support."""

        flags = InputMode(
            int(self.properties[DeviceAttribute.PLAYMODE_SUPPORT], base=16)
        )
        return [INPUT_MODE_MAP[flag] for flag in flags]

    @property
    def eth(self) -> str:
        """Returns the ethernet address."""
        return (
            self.properties[DeviceAttribute.ETH_DHCP]
            if DeviceAttribute.ETH_DHCP in self.properties
            else self.properties[DeviceAttribute.ETH0]
        )


class LinkPlayPlayer:
    """Represents a LinkPlay player."""

    bridge: LinkPlayBridge
    properties: dict[PlayerAttribute, str] = dict.fromkeys(
        PlayerAttribute.__members__.values(), ""
    )

    def __init__(self, bridge: LinkPlayBridge):
        self.bridge = bridge

    async def update_status(self) -> None:
        """Update the player status."""
        properties: dict[PlayerAttribute, str] = await self.bridge.json_request(
            LinkPlayCommand.PLAYER_STATUS
        )  # type: ignore[assignment]

        self.properties = fixup_player_properties(properties)

    async def next(self) -> None:
        """Play the next song in the playlist."""
        await self.bridge.request(LinkPlayCommand.NEXT)

    async def previous(self) -> None:
        """Play the previous song in the playlist."""
        await self.bridge.request(LinkPlayCommand.PREVIOUS)

    async def play(self, value: str) -> None:
        """Start playing the selected track."""
        await self.bridge.request(LinkPlayCommand.PLAY.format(value))  # type: ignore[str-format]

    async def resume(self) -> None:
        """Resume playing the current track."""
        await self.bridge.request(LinkPlayCommand.RESUME)

    async def mute(self) -> None:
        """Mute the player."""
        await self.bridge.request(LinkPlayCommand.MUTE)
        self.properties[PlayerAttribute.MUTED] = MuteMode.MUTED

    async def unmute(self) -> None:
        """Unmute the player."""
        await self.bridge.request(LinkPlayCommand.UNMUTE)
        self.properties[PlayerAttribute.MUTED] = MuteMode.UNMUTED

    async def play_playlist(self, index: int) -> None:
        """Start playing chosen playlist by index number."""
        await self.bridge.request(LinkPlayCommand.PLAYLIST.format(index))  # type: ignore[str-format]

    async def pause(self) -> None:
        """Pause the current playing track."""
        await self.bridge.request(LinkPlayCommand.PAUSE)
        self.properties[PlayerAttribute.PLAYING_STATUS] = PlayingStatus.PAUSED

    async def toggle(self) -> None:
        """Start playing if the player is currently not playing. Stops playing if it is."""
        await self.bridge.request(LinkPlayCommand.TOGGLE)

    async def set_volume(self, value: int) -> None:
        """Set the player volume."""
        if not 0 <= value <= 100:
            raise ValueError("Volume must be between 0 and 100.")

        await self.bridge.request(LinkPlayCommand.VOLUME.format(value))  # type: ignore[str-format]

    async def set_equalizer_mode(self, mode: EqualizerMode) -> None:
        """Set the equalizer mode."""
        await self.bridge.request(LinkPlayCommand.EQUALIZER_MODE.format(mode))  # type: ignore[str-format]

    async def set_loop_mode(self, mode: LoopMode) -> None:
        """Set the loop mode."""
        await self.bridge.request(LinkPlayCommand.LOOP_MODE.format(mode))  # type: ignore[str-format]

    async def set_play_mode(self, mode: PlayingMode) -> None:
        """Set the play mode."""
        await self.bridge.request(
            LinkPlayCommand.SWITCH_MODE.format(PLAY_MODE_SEND_MAP[mode])
        )  # type: ignore[str-format]

    async def play_preset(self, preset_number: int) -> None:
        """Play a preset."""
        if not 0 < preset_number <= 10:
            raise ValueError("Preset must be between 1 and 10.")
        await self.bridge.request(LinkPlayCommand.PLAY_PRESET.format(preset_number))

    @property
    def muted(self) -> bool:
        """Returns if the player is muted."""
        return (
            self.properties.get(PlayerAttribute.MUTED, MuteMode.UNMUTED)
            == MuteMode.MUTED
        )

    @property
    def title(self) -> str:
        """Returns if the currently playing title of the track."""
        return self.properties.get(PlayerAttribute.TITLE, "")

    @property
    def artist(self) -> str:
        """Returns if the currently playing artist."""
        return self.properties.get(PlayerAttribute.ARTIST, "")

    @property
    def album(self) -> str:
        """Returns if the currently playing album."""
        return self.properties.get(PlayerAttribute.ALBUM, "")

    @property
    def volume(self) -> int:
        """Returns the player volume, expressed in %."""
        return int(self.properties.get(PlayerAttribute.VOLUME, 0))

    @property
    def current_position(self) -> int:
        """Returns the current position of the track in milliseconds."""
        return int(self.properties.get(PlayerAttribute.CURRENT_POSITION, 0))

    @property
    def total_length(self) -> int:
        """Returns the total length of the track in milliseconds."""
        return int(self.properties.get(PlayerAttribute.TOTAL_LENGTH, 0))

    @property
    def status(self) -> PlayingStatus:
        """Returns the current playing status."""
        return PlayingStatus(
            self.properties.get(PlayerAttribute.PLAYING_STATUS, PlayingStatus.STOPPED)
        )

    @property
    def equalizer_mode(self) -> EqualizerMode:
        """Returns the current equalizer mode."""
        return EqualizerMode(
            self.properties.get(PlayerAttribute.EQUALIZER_MODE, EqualizerMode.CLASSIC)
        )

    @property
    def speaker_type(self) -> SpeakerType:
        """Returns the current speaker the player is playing on."""
        return SpeakerType(
            self.properties.get(PlayerAttribute.SPEAKER_TYPE, SpeakerType.MAIN_SPEAKER)
        )

    @property
    def channel_type(self) -> ChannelType:
        """Returns the channel the player is playing on."""
        return ChannelType(
            self.properties.get(PlayerAttribute.CHANNEL_TYPE, ChannelType.STEREO)
        )

    @property
    def play_mode(self) -> PlayingMode:
        """Returns the current playing mode of the player."""
        try:
            return PlayingMode(
                self.properties.get(PlayerAttribute.PLAYBACK_MODE, PlayingMode.IDLE)
            )
        except ValueError:
            return PlayingMode(PlayingMode.IDLE)

    @property
    def loop_mode(self) -> LoopMode:
        """Returns the current playlist mode."""
        return LoopMode(
            self.properties.get(
                PlayerAttribute.PLAYLIST_MODE, LoopMode.CONTINUOUS_PLAYBACK
            )
        )


class LinkPlayBridge:
    """Represents a LinkPlay bridge to control the device and player attached to it."""

    endpoint: LinkPlayEndpoint
    device: LinkPlayDevice
    player: LinkPlayPlayer

    def __init__(self, *, endpoint: LinkPlayEndpoint):
        self.endpoint = endpoint
        self.device = LinkPlayDevice(self)
        self.player = LinkPlayPlayer(self)

    def __str__(self) -> str:
        if self.device.name == "":
            return f"{self.endpoint}"

        return self.device.name

    async def json_request(self, command: str) -> dict[str, str]:
        """Performs a GET request on the given command and returns the result as a JSON object."""
        return await self.endpoint.json_request(command)

    async def request(self, command: str) -> None:
        """Performs a GET request on the given command and verifies the result."""
        await self.endpoint.request(command)


class LinkPlayMultiroom:
    """Represents a LinkPlay multiroom group. Contains a leader and a list of followers.
    The leader is the device that controls the group."""

    leader: LinkPlayBridge
    followers: list[LinkPlayBridge]

    def __init__(self, leader: LinkPlayBridge):
        self.leader = leader
        self.followers = []

    async def update_status(self, bridges: list[LinkPlayBridge]) -> None:
        """Updates the multiroom status."""
        properties: dict[Any, Any] = await self.leader.json_request(
            LinkPlayCommand.MULTIROOM_LIST
        )

        self.followers = []
        if int(properties[MultiroomAttribute.NUM_FOLLOWERS]) == 0:
            return

        follower_uuids = [
            follower[MultiroomAttribute.UUID]
            for follower in properties[MultiroomAttribute.FOLLOWER_LIST]
        ]
        new_followers = [
            bridge for bridge in bridges if bridge.device.uuid in follower_uuids
        ]
        self.followers.extend(new_followers)

    async def ungroup(self) -> None:
        """Ungroups the multiroom group."""
        await self.leader.request(LinkPlayCommand.MULTIROOM_UNGROUP)
        self.followers = []

    async def add_follower(self, follower: LinkPlayBridge) -> None:
        """Adds a follower to the multiroom group."""
        await follower.request(
            LinkPlayCommand.MULTIROOM_JOIN.format(self.leader.device.eth)
        )  # type: ignore[str-format]
        self.followers.append(follower)

    async def remove_follower(self, follower: LinkPlayBridge) -> None:
        """Removes a follower from the multiroom group."""
        await self.leader.request(
            LinkPlayCommand.MULTIROOM_KICK.format(follower.device.eth)
        )  # type: ignore[str-format]
        self.followers.remove(follower)

    async def set_volume(self, value: int) -> None:
        """Sets the volume for the multiroom group."""
        if not 0 <= value <= 100:
            raise ValueError("Volume must be between 0 and 100")

        str_vol = str(value)
        await self.leader.request(LinkPlayCommand.MULTIROOM_VOL.format(str_vol))  # type: ignore[str-format]

        for bridge in [self.leader] + self.followers:
            bridge.player.properties[PlayerAttribute.VOLUME] = str_vol

    async def mute(self) -> None:
        """Mutes the multiroom group."""
        await self.leader.request(LinkPlayCommand.MULTIROOM_MUTE)

    async def unmute(self) -> None:
        """Unmutes the multiroom group."""
        await self.leader.request(LinkPlayCommand.MULTIROOM_UNMUTE)
