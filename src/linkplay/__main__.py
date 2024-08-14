import asyncio

from linkplay.controller import LinkPlayController
from linkplay.utils import async_create_unverified_client_session


async def main():
    async with await async_create_unverified_client_session() as session:
        controller = LinkPlayController(session)

        await controller.discover_bridges()
        for bridge in controller.bridges:
            print(bridge)

        await controller.discover_multirooms()
        for multiroom in controller.multirooms:
            print(multiroom.followers)


if __name__ == "__main__":
    asyncio.run(main())
