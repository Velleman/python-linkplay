from enum import StrEnum

API_ENDPOINT: str = "{}/httpapi.asp?command={}"
API_TIMEOUT = 2


class LinkPlayCommand(StrEnum):
    DEVICE_STATUS = "getStatus"
    SYSLOG = "getsyslog"
    UPDATE_SERVER = "GetUpdateServer"
    PLAYER_STATUS = "getPlayerStatus"
    NEXT = "setPlayerCmd:next"
    PREVIOUS = "setPlayerCmd:prev"
    UNMUTE = "setPlayerCmd:mute:0"
    MUTE = "setPlayerCmd:mute:1"
    RESUME = "setPlayerCmd:resume"
    PLAY = "setPlayerCmd:play:{}"
    SEEK = "setPlayerCmd:seek:{}"
    VOL = "setPlayerCmd:vol:{}"


class SpeakerType(StrEnum):
    """Defines the speaker type."""
    MAIN_SPEAKER = "0"
    SUB_SPEAKER = "1"


class ChannelType(StrEnum):
    """Defines the channel type."""
    STEREO = "0"
    LEFT_CHANNEL = "1"
    RIGHT_CHANNEL = "2"


class PlaybackMode(StrEnum):
    """Defines the playback mode."""
    NONE = "0"
    WIIMU = "10"
    HTTP = "20"


class PlaylistMode(StrEnum):
    """Defines the playlist mode."""
    CONTINOUS_PLAY_ONE_SONG = "-1"
    PLAY_IN_ORDER = "0"
    CONTINUOUS_PLAYBACK = "1"
    RANDOM_PLAYBACK = "2"
    LIST_CYCLE = "3"


class EqualizerMode(StrEnum):
    """Defines the equalizer mode."""
    NONE = "0"
    CLASSIC = "1"
    POP = "2"
    JAZZ = "3"
    VOCAL = "4"


class PlayingStatus(StrEnum):
    """Defines the playing status."""
    PLAYING = "play"
    LOADING = "load"
    STOPPED = "stop"
    PAUSED = "pause"


class PlayerStatus(StrEnum):
    SPEAKER_TYPE = "type"
    CHANNEL_TYPE = "ch"
    PLAYBACK_MODE = "mode"
    PLAYLIST_MODE = "loop"
    EQUALIZER_MODE = "eq"
    PLAYING_STATUS = "status"
    CURRENT_POSITION = "curpos"
    OFFSET_POSITION = "offset_pts"
    TOTAL_LENGTH = "totlen"
    TITLE = "Title"
    ARTIST = "Artist"
    ALBUM = "Album"
    ALARM_FLAG = "alarmflag"
    PLAYLIST_COUNT = "plicount"
    PLAYLIST_INDEX = "plicurr"
    VOLUME = "vol"
    MUTED = "mute"


class DeviceStatus(StrEnum):
    UUID = "uuid"
