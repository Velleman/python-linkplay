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

    def get_bridge_callback(self):
        """Returns an async callback function for LinkPlayBridge."""

        async def callback():
            """Async callback function to handle events from a LinkPlayBridge."""
            LOGGER.debug("Controller event received")
            await self.discover_multirooms()

        return callback

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

    async def find_bridge(self, bridge_uuid: str) -> LinkPlayBridge | None:
        """Find a LinkPlay device by its bridge uuid."""

        for bridge in self.bridges:
            if bridge.device.uuid == bridge_uuid:
                return bridge

        return None

    async def add_bridge(self, bridge_to_add: LinkPlayBridge) -> None:
        """Add given LinkPlay device if not already added."""

        # Add bridge
        current_bridges = [bridge.device.uuid for bridge in self.bridges]
        if bridge_to_add.device.uuid not in current_bridges:
            bridge_to_add.device.set_callback(self.get_bridge_callback())
            self.bridges.append(bridge_to_add)

    async def remove_bridge(self, bridge_to_remove: LinkPlayBridge) -> None:
        """Remove given LinkPlay device if not already deleted."""

        # Remove bridge
        current_bridges = [bridge.device.uuid for bridge in self.bridges]
        if bridge_to_remove.device.uuid in current_bridges:
            self.bridges.remove(bridge_to_remove)

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
                multiroom.leader.multiroom = None
                removed_multirooms.append(multiroom)
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
