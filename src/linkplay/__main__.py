import asyncio
import aiohttp

from linkplay.consts import PlayerStatus
from linkplay.discovery import discover_linkplay_devices

async def main():
    async with aiohttp.ClientSession() as session:
        bridges = await discover_linkplay_devices(session)

        if len(bridges) > 0:
            bridge = bridges[0]
            await bridge.set_volume(session, 100)
            print(f"{bridge}: {bridge.player_status[PlayerStatus.ARTIST]} - {bridge.player_status[PlayerStatus.TITLE]} - {bridge.volume}%")

if __name__ == "__main__":
    asyncio.run(main())
