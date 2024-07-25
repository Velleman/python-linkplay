import asyncio
import aiohttp

from linkplay.controller import LinkPlayController


async def main():
    async with aiohttp.ClientSession() as session:
        controller = LinkPlayController(session)

        await controller.discover_bridges()
        for bridge in controller.bridges:
            print(bridge)

        await controller.discover_multirooms()
        for multiroom in controller.multirooms:
            print(multiroom.followers)


if __name__ == "__main__":
    asyncio.run(main())
