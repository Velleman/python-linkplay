import asyncio

import aiohttp

from linkplay.discovery import discover_linkplay_bridges, discover_multirooms


async def main():
    async with aiohttp.ClientSession() as session:
        bridges = await discover_linkplay_bridges(session)
        multirooms = await discover_multirooms(bridges)
        print(multirooms)

if __name__ == "__main__":
    asyncio.run(main())
