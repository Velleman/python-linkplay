from enum import StrEnum, IntFlag
from typing import Dict

API_ENDPOINT: str = "{}/httpapi.asp?command={}"
API_TIMEOUT: int = 2
UNKNOWN_TRACK_PLAYING: str = "Unknown"
UPNP_DEVICE_TYPE = 'urn:schemas-upnp-org:device:MediaRenderer:1'


class LinkPlayCommand(StrEnum):
    """Defines the LinkPlay commands."""
    DEVICE_STATUS = "getStatus"
    SYSLOG = "getsyslog"
    UPDATE_SERVER = "GetUpdateServer"
    REBOOT = "reboot"
    PLAYER_STATUS = "getPlayerStatus"
    NEXT = "setPlayerCmd:next"
    PREVIOUS = "setPlayerCmd:prev"
    UNMUTE = "setPlayerCmd:mute:0"
    MUTE = "setPlayerCmd:mute:1"
    RESUME = "setPlayerCmd:resume"
    PLAY = "setPlayerCmd:play:{}"
    SEEK = "setPlayerCmd:seek:{}"
    VOLUME = "setPlayerCmd:vol:{}"
    PLAYLIST = "setPlayerCmd:playlist:uri:{}"
    PAUSE = "setPlayerCmd:pause"
    TOGGLE = "setPlayerCmd:onepause"
    EQUALIZER_MODE = "setPlayerCmd:equalizer:{}"
    LOOP_MODE = "setPlayerCmd:loopmode:{}"
    SWITCH_MODE = "setPlayerCmd:switchmode:{}"
    M3U_PLAYLIST = "setPlayerCmd:m3u:play:{}"
    MULTIROOM_LIST = "multiroom:getSlaveList"


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
    IDLE = "-1"
    NONE = "0"
    AIRPLAY = "1"
    DLNA = "2"
    QPLAY = "3"
    NETWORK = "10"
    WIIMU_LOCAL = "11"
    WIIMU_STATION = "12"
    WIIMU_RADIO = "13"
    WIIMU_SONGLIST = "14"
    TF_CARD_1 = "16"
    WIIMU_MAX = "19"
    API = "20"
    UDISK = "21"
    HTTP_MAX = "29"
    ALARM = "30"
    SPOTIFY = "31"
    LINE_IN = "40"
    BLUETOOTH = "41"
    EXT_LOCAL = "42"
    OPTICAL = "43"
    RCA = "44"
    CO_AXIAL = "45"
    FM = "46"
    LINE_IN_2 = "47"
    XLR = "48"
    HDMI = "49"
    MIRROR = "50"
    USB_DAC = "51"
    TF_CARD_2 = "52"
    TALK = "60"
    SLAVE = "99"


PLAYBACK_MODE_MAP: Dict[PlaybackMode, str] = {
    PlaybackMode.IDLE: 'Idle',
    PlaybackMode.NONE: 'Idle',
    PlaybackMode.AIRPLAY: 'Airplay',
    PlaybackMode.DLNA: 'DLNA',
    PlaybackMode.QPLAY: 'QPlay',
    PlaybackMode.NETWORK: 'wifi',
    PlaybackMode.WIIMU_LOCAL: 'udisk',
    PlaybackMode.TF_CARD_1: 'TFcard',
    PlaybackMode.API: 'API',
    PlaybackMode.UDISK: 'udisk',
    PlaybackMode.ALARM: 'Alarm',
    PlaybackMode.SPOTIFY: 'Spotify',
    PlaybackMode.LINE_IN: 'line-in',
    PlaybackMode.BLUETOOTH: 'bluetooth',
    PlaybackMode.OPTICAL: 'optical',
    PlaybackMode.RCA: 'RCA',
    PlaybackMode.CO_AXIAL: 'co-axial',
    PlaybackMode.FM: 'FM',
    PlaybackMode.LINE_IN_2: 'line-in2',
    PlaybackMode.XLR: 'XLR',
    PlaybackMode.HDMI: 'HDMI',
    PlaybackMode.MIRROR: 'cd',
    PlaybackMode.USB_DAC: 'USB DAC',
    PlaybackMode.TF_CARD_2: 'TFcard',
    PlaybackMode.TALK: 'Talk',
    PlaybackMode.SLAVE: 'Idle'
}


class LoopMode(StrEnum):
    """Defines the loop mode."""
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


class MuteMode(StrEnum):
    """Defines the mute mode."""
    UNMUTED = "0"
    MUTED = "1"


class PlaymodeSupport(IntFlag):
    """Defines which modes the player supports."""
    LINE_IN = 2
    BLUETOOTH = 4
    USB = 8
    OPTICAL = 16
    COAXIAL = 64
    LINE_IN_2 = 256
    USBDAC = 32768
    OPTICAL_2 = 262144


class PlayerAttribute(StrEnum):
    """Defines the player attributes."""
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


class DeviceAttribute(StrEnum):
    """Defines the device attributes."""
    UUID = "uuid"
    DEVICE_NAME = "DeviceName"
    GROUP_NAME = "GroupName"
    SSID = "ssid"
    LANGUAGE = "language"
    FIRMWARE = "firmware"
    HARDWARE = "hardware"
    BUILD = "build"
    PROJECT = "project"
    PRIV_PRJ = "priv_prj"
    PROJECT_BUILD_NAME = "project_build_name"
    RELEASE = "Release"
    TEMP_UUID = "temp_uuid"
    HIDE_SSID = "hideSSID"
    SSID_STRATEGY = "SSIDStrategy"
    BRANCH = "branch"
    GROUP = "group"
    WMRM_VERSION = "wmrm_version"
    INTERNET = "internet"
    MAC_ADDRESS = "MAC"
    STA_MAC_ADDRESS = "STA_MAC"
    COUNTRY_CODE = "CountryCode"
    COUNTRY_REGION = "CountryRegion"
    NET_STAT = "netstat"
    ESSID = "essid"
    APCLI0 = "apcli0"
    ETH2 = "eth2"
    RA0 = "ra0"
    ETH_DHCP = "eth_dhcp"
    VERSION_UPDATE = "VersionUpdate"
    NEW_VER = "NewVer"
    SET_DNS_ENABLE = "set_dns_enable"
    MCU_VER = "mcu_ver"
    MCU_VER_NEW = "mcu_ver_new"
    DSP_VER = "dsp_ver"
    DSP_VER_NEW = "dsp_ver_new"
    DATE = "date"
    TIME = "time"
    TIMEZONE = "tz"
    DST_ENABLE = "dst_enable"
    REGION = "region"
    PROMPT_STATUS = "prompt_status"
    IOT_VER = "iot_ver"
    UPNP_VERSION = "upnp_version"
    CAP1 = "cap1"
    CAPABILITY = "capability"
    LANGUAGES = "languages"
    STREAMS_ALL = "streams_all"
    STREAMS = "streams"
    EXTERNAL = "external"
    PLAYMODE_SUPPORT = "plm_support"
    PRESET_KEY = "preset_key"
    SPOTIFY_ACTIVE = "spotify_active"
    LBC_SUPPORT = "lbc_support"
    PRIVACY_MODE = "privacy_mode"
    WIFI_CHANNEL = "WifiChannel"
    RSSI = "RSSI"
    BSSID = "BSSID"
    BATTERY = "battery"
    BATTERY_PERCENT = "battery_percent"
    SECURE_MODE = "securemode"
    AUTH = "auth"
    ENCRYPTION = "encry"
    UPNP_UUID = "upnp_uuid"
    UART_PASS_PORT = "uart_pass_port"
    COMMUNICATION_PORT = "communication_port"
    WEB_FIRMWARE_UPDATE_HIDE = "web_firmware_update_hide"
    IGNORE_TALKSTART = "ignore_talkstart"
    WEB_LOGIN_RESULT = "web_login_result"
    SILENCE_OTA_TIME = "silenceOTATime"
    IGNORE_SILENCE_OTA_TIME = "ignore_silenceOTATime"
    NEW_TUNEIN_PRESET_AND_ALARM = "new_tunein_preset_and_alarm"
    IHEARTRADIO_NEW = "iheartradio_new"
    NEW_IHEART_PODCAST = "new_iheart_podcast"
    TIDAL_VERSION = "tidal_version"
    SERVICE_VERSION = "service_version"
    ETH_MAC_ADDRESS = "ETH_MAC"
    SECURITY = "security"
    SECURITY_VERSION = "security_version"

class MultiroomAttribute(StrEnum):
    """Defines the player attributes."""
    NUM_FOLLOWERS = "slaves"
    FOLLOWER_LIST = "slave_list"
    UUID = "uuid"
