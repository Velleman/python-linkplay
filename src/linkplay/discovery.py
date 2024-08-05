from typing import Any

from aiohttp import ClientSession
from async_upnp_client.search import async_search
from async_upnp_client.utils import CaseInsensitiveDict
from deprecated import deprecated

from linkplay.bridge import LinkPlayBridge
from linkplay.consts import UPNP_DEVICE_TYPE, LinkPlayCommand, MultiroomAttribute
from linkplay.endpoint import LinkPlayApiEndpoint, LinkPlayEndpoint
from linkplay.exceptions import LinkPlayRequestException


@deprecated(
    reason="Use linkplay_factory_bridge_endpoint with a LinkPlayEndpoint or linkplay_factory_httpapi_bridge instead.",
    version="0.0.7",
)
async def linkplay_factory_bridge(
    ip_address: str, session: ClientSession
) -> LinkPlayBridge | None:
    """Attempts to create a LinkPlayBridge from the given IP address.
    Returns None if the device is not an expected LinkPlay device."""
    endpoint: LinkPlayApiEndpoint = LinkPlayApiEndpoint(
        protocol="http", endpoint=ip_address, session=session
    )
    try:
        return await linkplay_factory_bridge_endpoint(endpoint)
    except LinkPlayRequestException:
        return None


async def linkplay_factory_bridge_endpoint(
    endpoint: LinkPlayEndpoint,
) -> LinkPlayBridge:
    """Attempts to create a LinkPlayBridge from given LinkPlayEndpoint.
    Raises LinkPlayRequestException if the device is not an expected LinkPlay device."""

    bridge: LinkPlayBridge = LinkPlayBridge(endpoint=endpoint)
    await bridge.device.update_status()
    await bridge.player.update_status()
    return bridge


async def linkplay_factory_httpapi_bridge(
    ip_address: str, session: ClientSession
) -> LinkPlayBridge:
    """Attempts to create a LinkPlayBridge from the given IP address.
    Attempts to use HTTPS first, then falls back to HTTP.
    Raises LinkPlayRequestException if the device is not an expected LinkPlay device."""

    https_endpoint: LinkPlayApiEndpoint = LinkPlayApiEndpoint(
        protocol="https", endpoint=ip_address, session=session
    )
    try:
        return await linkplay_factory_bridge_endpoint(https_endpoint)
    except LinkPlayRequestException:
        http_endpoint: LinkPlayApiEndpoint = LinkPlayApiEndpoint(
            protocol="http", endpoint=ip_address, session=session
        )
        return await linkplay_factory_bridge_endpoint(http_endpoint)


async def discover_linkplay_bridges(
    session: ClientSession, discovery_through_multiroom: bool = True
) -> list[LinkPlayBridge]:
    """Attempts to discover LinkPlay devices on the local network."""
    bridges: dict[str, LinkPlayBridge] = {}

    async def add_linkplay_device_to_list(upnp_device: CaseInsensitiveDict):
        ip_address: str | None = upnp_device.get("_host")

        if not ip_address:
            return

        try:
            bridge = await linkplay_factory_httpapi_bridge(ip_address, session)
            bridges[bridge.device.uuid] = bridge
        except LinkPlayRequestException:
            pass

    await async_search(
        search_target=UPNP_DEVICE_TYPE, async_callback=add_linkplay_device_to_list
    )

    # Discover additional bridges through grouped multirooms
    if discovery_through_multiroom:
        multiroom_discovered_bridges: dict[str, LinkPlayBridge] = {}
        for bridge in bridges.values():
            for new_bridge in await discover_bridges_through_multiroom(bridge, session):
                multiroom_discovered_bridges[new_bridge.device.uuid] = new_bridge

        bridges = bridges | multiroom_discovered_bridges

    return list(bridges.values())


async def discover_bridges_through_multiroom(
    bridge: LinkPlayBridge, session: ClientSession
) -> list[LinkPlayBridge]:
    """Discovers bridges through the multiroom of the provided bridge."""
    properties: dict[Any, Any] = await bridge.json_request(
        LinkPlayCommand.MULTIROOM_LIST
    )

    if int(properties[MultiroomAttribute.NUM_FOLLOWERS]) == 0:
        return []

    followers: list[LinkPlayBridge] = []
    for follower in properties[MultiroomAttribute.FOLLOWER_LIST]:
        try:
            new_bridge = await linkplay_factory_httpapi_bridge(
                follower[MultiroomAttribute.IP], session
            )
            followers.append(new_bridge)
        except LinkPlayRequestException:
            pass

    return followers
