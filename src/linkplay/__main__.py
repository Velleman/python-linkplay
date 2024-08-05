import asyncio
import socket
import ssl

import aiohttp

from linkplay.controller import LinkPlayController
from linkplay.utils import create_unverified_context


async def main():
    context: ssl.SSLContext = create_unverified_context()
    connector: aiohttp.TCPConnector = aiohttp.TCPConnector(
        family=socket.AF_UNSPEC, ssl=context
    )
    async with aiohttp.ClientSession(connector=connector) as session:
        controller = LinkPlayController(session)

        await controller.discover_bridges()
        for bridge in controller.bridges:
            print(bridge)

        await controller.discover_multirooms()
        for multiroom in controller.multirooms:
            print(multiroom.followers)


if __name__ == "__main__":
    asyncio.run(main())
