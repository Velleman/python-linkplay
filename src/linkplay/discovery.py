from typing import Any

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


async def discover_linkplay_bridges(session: ClientSession) -> list[LinkPlayBridge]:
    """Attempts to discover LinkPlay devices on the local network."""
    bridges: dict[str, LinkPlayBridge] = {}

    async def add_linkplay_device_to_list(upnp_device: CaseInsensitiveDict):
        ip_address: str | None = upnp_device.get('_host')

        if not ip_address:
            return

        if bridge := await linkplay_factory_bridge(ip_address, session):
            bridges[bridge.device.uuid] = bridge

    await async_search(
        search_target=UPNP_DEVICE_TYPE,
        async_callback=add_linkplay_device_to_list
    )

    # Discover additional bridges through grouped multirooms
    multiroom_discovered_bridges: dict[str, LinkPlayBridge] = {}
    for bridge in bridges.values():
        for new_bridge in await discover_bridges_through_multiroom(bridge, session):
            multiroom_discovered_bridges[new_bridge.device.uuid] = new_bridge

    bridges = bridges | multiroom_discovered_bridges
    return list(bridges.values())


async def discover_multirooms(bridges: list[LinkPlayBridge]) -> list[LinkPlayMultiroom]:
    """Discovers multirooms through the list of provided bridges."""
    multirooms: list[LinkPlayMultiroom] = []
    bridges_dict: dict[str, LinkPlayBridge] = {bridge.device.uuid: bridge for bridge in bridges}

    for bridge in bridges:
        properties: dict[Any, Any] = await bridge.json_request(LinkPlayCommand.MULTIROOM_LIST)

        if int(properties[MultiroomAttribute.NUM_FOLLOWERS]) == 0:
            continue

        followers: list[LinkPlayBridge] = []
        for follower in properties[MultiroomAttribute.FOLLOWER_LIST]:
            if follower[MultiroomAttribute.UUID] in bridges_dict:
                followers.append(bridges_dict[follower[MultiroomAttribute.UUID]])

        multirooms.append(LinkPlayMultiroom(bridge, followers))

    return multirooms


async def discover_bridges_through_multiroom(bridge: LinkPlayBridge,
                                             session: ClientSession) -> list[LinkPlayBridge]:
    """Discovers bridges through the multiroom of the provided bridge."""
    properties: dict[Any, Any] = await bridge.json_request(LinkPlayCommand.MULTIROOM_LIST)

    if int(properties[MultiroomAttribute.NUM_FOLLOWERS]) == 0:
        return []

    followers: list[LinkPlayBridge] = []
    for follower in properties[MultiroomAttribute.FOLLOWER_LIST]:
        if new_bridge := await linkplay_factory_bridge(follower[MultiroomAttribute.IP], session):
            followers.append(new_bridge)

    return followers
