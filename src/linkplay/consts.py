from enum import IntFlag, StrEnum

API_ENDPOINT: str = "{}/httpapi.asp?command={}"
API_TIMEOUT: int = 2
UNKNOWN_TRACK_PLAYING: str = "Unknown"
UPNP_DEVICE_TYPE = "urn:schemas-upnp-org:device:MediaRenderer:1"

MTLS_CERTIFICATE_CONTENTS = """
-----BEGIN PRIVATE KEY-----
MIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQCk/u2tH0LwCOv8
JmqLvQdjNAdkxfSCPwrdHM7STlq5xaJGQe29yd8kjP7h0wERkeO/9JO62wUHBu0P
WIsS/jwLG+G3oAU+7BNfjmBhDXyHIRQLzAWEbtxbsSTke1losfvlQXGumXrMqf9X
LdIYvbA53mp8GImQbJkaCDvwnEdUFkuJ0W5Tofr58jJqfCt6OPwHmnP4oC6LpPtJ
YDy7r1Q9sLgCYEtDEw/Mhf+mKuC0pnst52e1qceVjvCuUBoeuhk6kpnEbpSdEKbD
bdE8cPoVRmrj1//PLFMVtNB7k2aPMb3CcoJ/dHxaCXwk9b3jIBs6CyWixN92CuaO
Q98Ug/YlAgMBAAECggEAHyCpHlwjeL12J9/nge1rk1+hdXWTJ29VUVm5+xslKp8K
ek6912xaWL7w5xGzxejMGs69gCcJz8WSu65srmygT0g3UTkzRCetj/2AWU7+C1BG
Q+N9tvpjQDkvSJusxn+tkhbCp7n03N/FeGEAngJLWN+JH1hRu5mBWNPs2vvgyRAO
Cv95G7uENavCUXcyYsKPoAfz3ebD/idwwWW2RKAd0ufYeafiFC0ImTLcpEjBvCTW
UoAniBSVx1PHK4IAUb3pMdPtIv1uBlIMotHS/GdEyHU6qOsX5ijHqncHHneaytmL
+wJukPqASEBl3F2UnzryBUgGqr1wyH9vtPGjklnngQKBgQDZv3oxZWul//2LV+jo
ZipbnP6nwG3J6pOWPDD3dHoZ6Q2DRyJXN5ty40PS393GVvrSJSdRGeD9+ox5sFoj
iUMgd6kHG4ME7Fre57zUkqy1Ln1K1fkP5tBUD0hviigHBWih2/Nyl2vrdvX5Wpxx
5r42UQa9nOzrNB03DTOhDrUszQKBgQDB+xdMRNSFfCatQj+y2KehcH9kaANPvT0l
l9vgb72qks01h05GSPBZnT1qfndh/Myno9KuVPhJ0HrVwRAjZTd4T69fAH3imW+R
7HP+RgDen4SRTxj6UTJh2KZ8fdPeCby1xTwxYNjq8HqpiO6FHZpE+l4FE8FalZK+
Z3GhE7DuuQKBgDq7b+0U6xVKWAwWuSa+L9yoGvQKblKRKB/Uumx0iV6lwtRPAo89
23sAm9GsOnh+C4dVKCay8UHwK6XDEH0XT/jY7cmR/SP90IDhRsibi2QPVxIxZs2I
N1cFDEexnxxNtCw8VIzrFNvdKXmJnDsIvvONpWDNjAXg96RatjtR6UJdAoGBAIAx
HU5r1j54s16gf1QD1ZPcsnN6QWX622PynX4OmjsVVMPhLRtJrHysax/rf52j4OOQ
YfSPdp3hRqvoMHATvbqmfnC79HVBjPfUWTtaq8xzgro8mXcjHbaH5E41IUSFDs7Z
D1Raej+YuJc9RNN3orGe+29DhO4GFrn5xp/6UV0RAoGBAKUdRgryWzaN4auzWaRD
lxoMhlwQdCXzBI1YLH2QUL8elJOHMNfmja5G9iW07ZrhhvQBGNDXFbFrX4hI3c/0
JC3SPhaaedIjOe9Qd3tn5KgYxbBnWnCTt0kxgro+OM3ORgJseSWbKdRrjOkUxkab
/NDvel7IF63U4UEkrVVt1bYg
-----END PRIVATE KEY-----
-----BEGIN CERTIFICATE-----
MIIDmDCCAoACAQEwDQYJKoZIhvcNAQELBQAwgZExCzAJBgNVBAYTAkNOMREwDwYD
VQQIDAhTaGFuZ2hhaTERMA8GA1UEBwwIU2hhbmdoYWkxETAPBgNVBAoMCExpbmtw
bGF5MQwwCgYDVQQLDANpbmMxGTAXBgNVBAMMEHd3dy5saW5rcGxheS5jb20xIDAe
BgkqhkiG9w0BCQEWEW1haWxAbGlua3BsYXkuY29tMB4XDTE4MTExNTAzMzI1OVoX
DTQ2MDQwMTAzMzI1OVowgZExCzAJBgNVBAYTAkNOMREwDwYDVQQIDAhTaGFuZ2hh
aTERMA8GA1UEBwwIU2hhbmdoYWkxETAPBgNVBAoMCExpbmtwbGF5MQwwCgYDVQQL
DANpbmMxGTAXBgNVBAMMEHd3dy5saW5rcGxheS5jb20xIDAeBgkqhkiG9w0BCQEW
EW1haWxAbGlua3BsYXkuY29tMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKC
AQEApP7trR9C8Ajr/CZqi70HYzQHZMX0gj8K3RzO0k5aucWiRkHtvcnfJIz+4dMB
EZHjv/STutsFBwbtD1iLEv48Cxvht6AFPuwTX45gYQ18hyEUC8wFhG7cW7Ek5HtZ
aLH75UFxrpl6zKn/Vy3SGL2wOd5qfBiJkGyZGgg78JxHVBZLidFuU6H6+fIyanwr
ejj8B5pz+KAui6T7SWA8u69UPbC4AmBLQxMPzIX/pirgtKZ7LedntanHlY7wrlAa
HroZOpKZxG6UnRCmw23RPHD6FUZq49f/zyxTFbTQe5NmjzG9wnKCf3R8Wgl8JPW9
4yAbOgslosTfdgrmjkPfFIP2JQIDAQABMA0GCSqGSIb3DQEBCwUAA4IBAQARmy6f
esrifhW5NM9i3xsEVp945iSXhqHgrtIROgrC7F1EIAyoIiBdaOvitZVtsYc7Ivys
QtyVmEGscyjuYTdfigvwTVVj2oCeFv1Xjf+t/kSuk6X3XYzaxPPnFG4nAe2VwghE
rbZG0K5l8iXM7Lm+ZdqQaAYVWsQDBG8lbczgkB9q5ed4zbDPf6Fsrsynxji/+xa4
9ARfyHlkCDBThGNnnl+QITtfOWxm/+eReILUQjhwX+UwbY07q/nUxLlK6yrzyjnn
wi2B2GovofQ/4icVZ3ecTqYK3q9gEtJi72V+dVHM9kSA4Upy28Y0U1v56uoqeWQ6
uc2m8y8O/hXPSfKd
-----END CERTIFICATE-----
"""

class LinkPlayCommand(StrEnum):
    """Defines the LinkPlay commands."""

    DEVICE_STATUS = "getStatusEx"
    SYSLOG = "getsyslog"
    UPDATE_SERVER = "GetUpdateServer"
    REBOOT = "reboot"
    PLAYER_STATUS = "getPlayerStatusEx"
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
    MULTIROOM_UNGROUP = "multiroom:ungroup"
    MULTIROOM_KICK = "multiroom:SlaveKickout:{}"
    MULTIROOM_VOL = "setPlayerCmd:slave_vol:{}"
    MULTIROOM_MUTE = "setPlayerCmd:slave_mute:mute"
    MULTIROOM_UNMUTE = "setPlayerCmd:slave_mute:unmute"
    MULTIROOM_JOIN = "ConnectMasterAp:JoinGroupMaster:eth{}:wifi0.0.0.0"


class SpeakerType(StrEnum):
    """Defines the speaker type."""

    MAIN_SPEAKER = "0"
    SUB_SPEAKER = "1"


class ChannelType(StrEnum):
    """Defines the channel type."""

    STEREO = "0"
    LEFT_CHANNEL = "1"
    RIGHT_CHANNEL = "2"


class PlayingMode(StrEnum):
    """Defines a possible playing mode."""

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
    COAXIAL = "45"
    FM = "46"
    LINE_IN_2 = "47"
    XLR = "48"
    HDMI = "49"
    MIRROR = "50"
    USB_DAC = "51"
    TF_CARD_2 = "52"
    OPTICAL_2 = "56"
    TALK = "60"
    SLAVE = "99"


# Map between a play mode and how to activate the play mode
PLAY_MODE_SEND_MAP: dict[PlayingMode, str] = {  # case sensitive!
    PlayingMode.NONE: "Idle",
    PlayingMode.AIRPLAY: "Airplay",
    PlayingMode.DLNA: "DLNA",
    PlayingMode.QPLAY: "QPlay",
    PlayingMode.NETWORK: "wifi",
    PlayingMode.WIIMU_LOCAL: "udisk",
    PlayingMode.TF_CARD_1: "TFcard",
    PlayingMode.API: "API",
    PlayingMode.UDISK: "udisk",
    PlayingMode.ALARM: "Alarm",
    PlayingMode.SPOTIFY: "Spotify",
    PlayingMode.LINE_IN: "line-in",
    PlayingMode.BLUETOOTH: "bluetooth",
    PlayingMode.OPTICAL: "optical",
    PlayingMode.RCA: "RCA",
    PlayingMode.COAXIAL: "co-axial",
    PlayingMode.FM: "FM",
    PlayingMode.LINE_IN_2: "line-in2",
    PlayingMode.XLR: "XLR",
    PlayingMode.HDMI: "HDMI",
    PlayingMode.MIRROR: "cd",
    PlayingMode.USB_DAC: "USB DAC",
    PlayingMode.TF_CARD_2: "TFcard",
    PlayingMode.TALK: "Talk",
    PlayingMode.SLAVE: "Idle",
    PlayingMode.OPTICAL_2: "optical2",
}


class LoopMode(StrEnum):
    """Defines the loop mode."""

    CONTINOUS_PLAY_ONE_SONG = "-1"
    PLAY_IN_ORDER = "0"
    CONTINUOUS_PLAYBACK = "1"
    RANDOM_PLAYBACK = "2"
    LIST_CYCLE = "3"
    SHUFF_DISABLED_REPEAT_DISABLED = "4"
    SHUFF_ENABLED_REPEAT_ENABLED_LOOP_ONCE = "5"


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


class InputMode(IntFlag):
    """Defines which inputs the player supports."""

    LINE_IN = 2
    BLUETOOTH = 4
    USB = 8
    OPTICAL = 16
    RCA = 32
    COAXIAL = 64
    LINE_IN_2 = 256
    USB_DAC = 32768
    OPTICAL_2 = 262144


# Map between the input modes and the play mode
INPUT_MODE_MAP: dict[InputMode, PlayingMode] = {
    InputMode.LINE_IN: PlayingMode.LINE_IN,
    InputMode.BLUETOOTH: PlayingMode.BLUETOOTH,
    InputMode.USB: PlayingMode.UDISK,
    InputMode.OPTICAL: PlayingMode.OPTICAL,
    InputMode.RCA: PlayingMode.RCA,
    InputMode.COAXIAL: PlayingMode.COAXIAL,
    InputMode.LINE_IN_2: PlayingMode.LINE_IN_2,
    InputMode.USB_DAC: PlayingMode.USB_DAC,
    InputMode.OPTICAL_2: PlayingMode.OPTICAL_2,
}


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
    IP = "ip"
