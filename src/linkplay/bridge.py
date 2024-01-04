from typing import Dict
from aiohttp import ClientSession

from linkplay.consts import LinkPlayCommand, DeviceStatus, PlayerStatus, API_ENDPOINT
from linkplay.utils import session_call_api


class LinkPlayBridge():
    """Represents a LinkPlay device."""

    protocol: str
    ip: str
    device_status: Dict[DeviceStatus, str]
    player_status: Dict[PlayerStatus, str]

    def __init__(self, protocol: str, ip: str, ):
        self.protocol = protocol
        self.ip = ip

    @property
    def endpoint(self) -> str:
        return API_ENDPOINT.format(self.protocol, self.ip)

    async def update_device_status(self, session: ClientSession):
        self.device_status = await session_call_api(self.endpoint, session, LinkPlayCommand.DEVICE_STATUS)

    async def update_player_status(self, session: ClientSession):
        status = await session_call_api(self.endpoint, session, LinkPlayCommand.PLAYER_STATUS)
        status[PlayerStatus.TITLE] = bytes.fromhex(status[PlayerStatus.TITLE]).decode("utf-8")
        status[PlayerStatus.ARTIST] = bytes.fromhex(status[PlayerStatus.ARTIST]).decode("utf-8")
        status[PlayerStatus.ALBUM] = bytes.fromhex(status[PlayerStatus.ALBUM]).decode("utf-8")
        self.player_status = status

    async def next(self, session: ClientSession):
        await session_call_api(self.endpoint, session, LinkPlayCommand.NEXT)

    async def previous(self, session: ClientSession):
        await session_call_api(self.endpoint, session, LinkPlayCommand.PREVIOUS)

    async def play(self, session: ClientSession, value: str):
        await session_call_api(self.endpoint, session, LinkPlayCommand.PLAY.format(value))

    async def resume(self, session: ClientSession):
        await session_call_api(self.endpoint, session, LinkPlayCommand.RESUME)

    async def mute(self, session: ClientSession):
        await session_call_api(self.endpoint, session, LinkPlayCommand.MUTE)

    async def unmute(self, session: ClientSession):
        await session_call_api(self.endpoint, session, LinkPlayCommand.UNMUTE)
