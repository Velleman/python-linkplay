import asyncio

import aiohttp

from linkplay.consts import EqualizerMode
from linkplay.discovery import linkplay_factory_bridge


async def main():
    async with aiohttp.ClientSession() as session:
        pass

if __name__ == "__main__":
    asyncio.run(main())
