from typing import Any, Dict, List

from aiohttp import ClientSession
from async_upnp_client.search import async_search
from async_upnp_client.utils import CaseInsensitiveDict

from linkplay.consts import UPNP_DEVICE_TYPE, LinkPlayCommand, MultiroomAttribute
from linkplay.bridge import LinkPlayBridge, LinkPlayMultiroom
from linkplay.exceptions import LinkPlayRequestException


async def linkplay_factory_bridge(ip_address: str, session: ClientSession) -> LinkPlayBridge | None:
    """Attempts to create a LinkPlayBridge from the given IP address.
    Returns None if the device is not an expected LinkPlay device."""
    bridge = LinkPlayBridge("http", ip_address, session)
    try:
        await bridge.device.update_status()
        await bridge.player.update_status()
    except LinkPlayRequestException:
        return None
    return bridge


async def discover_linkplay_bridges(session: ClientSession) -> List[LinkPlayBridge]:
    """Attempts to discover LinkPlay devices on the local network."""
    devices: List[LinkPlayBridge] = []

    async def add_linkplay_device_to_list(upnp_device: CaseInsensitiveDict):
        ip_address: str | None = upnp_device.get('_host')

        if not ip_address:
            return

        if bridge := await linkplay_factory_bridge(ip_address, session):
            devices.append(bridge)

    await async_search(
        search_target=UPNP_DEVICE_TYPE,
        async_callback=add_linkplay_device_to_list
    )

    return devices


async def discover_multirooms(bridges: List[LinkPlayBridge]) -> List[LinkPlayMultiroom]:
    """Discovers multirooms through the list of provided bridges."""
    multirooms: List[LinkPlayMultiroom] = []

    for bridge in bridges:
        properties: Dict[Any, Any] = await bridge.json_request(LinkPlayCommand.MULTIROOM_LIST)

        if int(properties[MultiroomAttribute.NUM_FOLLOWERS]) == 0:
            continue

        followers: List[LinkPlayBridge] = []
        for follower in properties[MultiroomAttribute.FOLLOWER_LIST]:
            follower_uuid = follower[MultiroomAttribute.UUID]
            follower_bridge = next((b for b in bridges if b.device.uuid == follower_uuid), None)
            if follower_bridge:
                followers.append(follower_bridge)

        multirooms.append(LinkPlayMultiroom(bridge, followers))

    return multirooms
