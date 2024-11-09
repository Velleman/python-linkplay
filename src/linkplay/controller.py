from aiohttp import ClientSession

from linkplay.bridge import LinkPlayBridge, LinkPlayMultiroom
from linkplay.consts import LOGGER
from linkplay.discovery import discover_linkplay_bridges
from linkplay.exceptions import LinkPlayInvalidDataException


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
            self.bridges.append(bridge_to_add)

    async def discover_multirooms(self) -> None:
        """Attempts to discover multirooms on the local network."""

        # Find and update existing multirooms
        multirooms = [
            bridge.multiroom
            for bridge in self.bridges
            if bridge.multiroom and bridge.multiroom.leader is bridge
        ]

        removed_multirooms = []
        for multiroom in multirooms:
            try:
                for follower in multiroom.followers:
                    follower.multiroom = None

                await multiroom.update_status(self.bridges)
                if len(multiroom.followers) > 0:
                    for follower in multiroom.followers:
                        follower.multiroom = multiroom
                else:
                    multiroom.leader.multiroom = None
                    removed_multirooms.append(multiroom)
            except LinkPlayInvalidDataException as exc:
                LOGGER.exception(exc)

        # Create new multirooms from new bridges
        for bridge in self.bridges:
            if bridge.multiroom:
                continue

            try:
                multiroom = LinkPlayMultiroom(bridge)
                await multiroom.update_status(self.bridges)
                if len(multiroom.followers) > 0:
                    multirooms.append(multiroom)
                    bridge.multiroom = multiroom
                    for follower in multiroom.followers:
                        follower.multiroom = multiroom
            except LinkPlayInvalidDataException as exc:
                LOGGER.exception(exc)

        # Remove multirooms with no followers
        multirooms = [item for item in multirooms if item not in removed_multirooms]

        # Update multirooms in controller
        self.multirooms = multirooms
