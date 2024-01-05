import asyncio

import aiohttp

from linkplay.discovery import discover_linkplay_devices


async def main():
    async with aiohttp.ClientSession() as session:
        devices = await discover_linkplay_devices(session)

if __name__ == "__main__":
    asyncio.run(main())
