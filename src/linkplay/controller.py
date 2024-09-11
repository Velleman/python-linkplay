from aiohttp import ClientSession

from linkplay.bridge import LinkPlayBridge, LinkPlayMultiroom
from linkplay.discovery import discover_linkplay_bridges


class LinkPlayController:
    """Represents a LinkPlay controller to manage the devices and multirooms."""

    session: ClientSession
    bridges: list[LinkPlayBridge]
    multirooms: list[LinkPlayMultiroom]

    def __init__(self, session: ClientSession):
        self.session = session
        self.bridges = []
        self.multirooms = []

    async def discover_bridges(self) -> None:
        """Attempts to discover LinkPlay devices on the local network."""

        # Discover new bridges
        discovered_bridges = await discover_linkplay_bridges(self.session)
        current_bridges = [bridge.device.uuid for bridge in self.bridges]
        new_bridges = [
            discovered_bridge
            for discovered_bridge in discovered_bridges
            if discovered_bridge.device.uuid not in current_bridges
        ]
        self.bridges.extend(new_bridges)

    async def add_bridge(self, bridge_to_add: LinkPlayBridge) -> None:
        """Add given LinkPlay device if not already added."""

        # Add bridge
        current_bridges = [bridge.device.uuid for bridge in self.bridges]
        if bridge_to_add.device.uuid not in current_bridges:
            self.bridges.extend(bridge_to_add)

    async def discover_multirooms(self) -> None:
        """Attempts to discover multirooms on the local network."""

        # Create new multirooms from new bridges
        new_multirooms = []
        for bridge in self.bridges:
            has_multiroom = any(
                multiroom for multiroom in self.multirooms if multiroom.leader == bridge
            )

            if has_multiroom:
                continue

            multiroom = LinkPlayMultiroom(bridge)
            await multiroom.update_status(self.bridges)
            if len(multiroom.followers) > 0:
                new_multirooms.append(multiroom)

        # Update existing multirooms
        for multiroom in self.multirooms:
            await multiroom.update_status(self.bridges)

        # Remove multirooms if they have no followers
        empty_multirooms = [
            multiroom for multiroom in self.multirooms if not multiroom.followers
        ]
        for empty_multiroom in empty_multirooms:
            self.multirooms.remove(empty_multiroom)

        # Add new multirooms
        self.multirooms.extend(new_multirooms)
