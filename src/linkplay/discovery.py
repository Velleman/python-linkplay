from typing import List, Optional
from aiohttp import ClientSession
from async_upnp_client.search import async_search
from async_upnp_client.utils import CaseInsensitiveDict

from linkplay.consts import UPNP_DEVICE_TYPE
from linkplay.bridge import LinkPlayBridge
from linkplay.exceptions import LinkPlayRequestException


async def linkplay_factory_bridge(ip: str, session: ClientSession) -> Optional[LinkPlayBridge]:
    """Attempts to create a LinkPlayBridge from the given IP address.
    Returns None if the device is not an expected LinkPlay device."""
    bridge = LinkPlayBridge("http", ip)
    try:
        await bridge.update_device_status(session)
        await bridge.update_player_status(session)
    except LinkPlayRequestException:
        return None
    return bridge


async def discover_linkplay_devices(session: ClientSession) -> List[LinkPlayBridge]:
    """Attempts to discover LinkPlay devices on the local network."""
    devices: List[LinkPlayBridge] = []
    async def add_linkplay_device_to_list(upnp_device: CaseInsensitiveDict):
        device_ip_address = upnp_device.get('_host')
        bridge = await linkplay_factory_bridge(device_ip_address, session)
        if bridge:
            devices.append(device_ip_address)

    await async_search(
        search_target=UPNP_DEVICE_TYPE,
        async_callback=add_linkplay_device_to_list
    )

    return devices
