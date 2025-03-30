from unittest.mock import AsyncMock, MagicMock

import pytest
from aiohttp import ClientSession
from linkplay.bridge import LinkPlayBridge, LinkPlayDevice, LinkPlayMultiroom
from linkplay.controller import LinkPlayController
from linkplay.exceptions import LinkPlayInvalidDataException


@pytest.fixture
def mock_session():
    return MagicMock(spec=ClientSession)


@pytest.fixture
def controller(mock_session):
    return LinkPlayController(mock_session)


@pytest.fixture
def mock_bridge():
    bridge = MagicMock(spec=LinkPlayBridge)
    bridge.device = MagicMock(spec=LinkPlayDevice)
    bridge.device.uuid = "mock-uuid"
    return bridge


@pytest.fixture
def mock_multiroom():
    multiroom = MagicMock(spec=LinkPlayMultiroom)
    multiroom.leader = MagicMock()
    multiroom.followers = []
    return multiroom


@pytest.mark.asyncio
async def test_add_bridge(controller, mock_bridge):
    await controller.add_bridge(mock_bridge)

    assert mock_bridge in controller.bridges


@pytest.mark.asyncio
async def test_add_bridge_already_exists(controller, mock_bridge):
    controller = LinkPlayController(mock_session)
    controller.bridges.append(mock_bridge)

    await controller.add_bridge(mock_bridge)

    assert controller.bridges.count(mock_bridge) == 1


@pytest.mark.asyncio
async def test_remove_bridge(controller, mock_bridge):
    controller.bridges.append(mock_bridge)

    await controller.remove_bridge(mock_bridge)

    assert mock_bridge not in controller.bridges


@pytest.mark.asyncio
async def test_remove_bridge_not_exists(controller, mock_bridge):
    await controller.remove_bridge(mock_bridge)

    assert mock_bridge not in controller.bridges
