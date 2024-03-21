from aiohttp import ClientSession

from linkplay.bridge import LinkPlayBridge, LinkPlayMultiroom
from linkplay.discovery import discover_linkplay_bridges


class LinkPlayController():
    """Represents a LinkPlay controller to manage the devices and multirooms."""

    session: ClientSession
    bridges: list[LinkPlayBridge]
    multirooms: list[LinkPlayMultiroom]

    def __init__(self, session: ClientSession):
        self.session = session
        self.bridges = []
        self.multirooms = []

    async def discover(self) -> None:
        """Attempts to discover LinkPlay devices on the local network."""

        # Discover new bridges
        discovered_bridges = await discover_linkplay_bridges(self.session)
        current_bridges = [bridge.device.uuid for bridge in self.bridges]
        new_bridges = [discovered_bridge for discovered_bridge in discovered_bridges if discovered_bridge.device.uuid not in current_bridges]
        self.bridges.extend(new_bridges)

        # Create new multirooms
        for new_bridge in new_bridges:
            self.multirooms.append(LinkPlayMultiroom(new_bridge))

        # Update multirooms
        for multiroom in self.multirooms:
            await multiroom.update_status(self.bridges)
