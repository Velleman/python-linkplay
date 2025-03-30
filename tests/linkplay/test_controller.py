from unittest.mock import AsyncMock, MagicMock, patch

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


@pytest.mark.asyncio
async def test_discover_bridges():
    """Test the discover_bridges method of LinkPlayController."""
    mock_session = ClientSession()
    controller = LinkPlayController(mock_session)

    # Mock the discover_linkplay_bridges function
    mock_bridge_1 = AsyncMock()
    mock_bridge_1.device.uuid = "uuid-1"
    mock_bridge_2 = AsyncMock()
    mock_bridge_2.device.uuid = "uuid-2"

    with patch(
        "linkplay.controller.discover_linkplay_bridges",
        return_value=[mock_bridge_1, mock_bridge_2],
    ) as mock_discover:
        # Call discover_bridges
        await controller.discover_bridges()

        # Assert discover_linkplay_bridges was called
        mock_discover.assert_called_once_with(mock_session)

        # Assert bridges were added to the controller
        assert len(controller.bridges) == 2
        assert controller.bridges[0].device.uuid == "uuid-1"
        assert controller.bridges[1].device.uuid == "uuid-2"

        # Call discover_bridges again with no new bridges
        await controller.discover_bridges()

        # Assert no duplicate bridges were added
        assert len(controller.bridges) == 2


@pytest.mark.asyncio
async def test_find_bridge_existing(controller, mock_bridge):
    """Test finding an existing bridge by UUID."""
    controller.bridges.append(mock_bridge)

    result = await controller.find_bridge("mock-uuid")
    assert result == mock_bridge


@pytest.mark.asyncio
async def test_find_bridge_non_existing(controller):
    """Test finding a non-existing bridge by UUID."""
    result = await controller.find_bridge("non-existent-uuid")
    assert result is None


@pytest.mark.asyncio
async def test_discover_multirooms_with_followers(
    controller, mock_bridge, mock_multiroom
):
    """Test discover_multirooms when multirooms with followers exist."""
    mock_bridge.multiroom = mock_multiroom
    mock_multiroom.leader = mock_bridge
    mock_multiroom.followers = [MagicMock(spec=LinkPlayBridge)]

    controller.bridges.append(mock_bridge)

    with patch.object(
        mock_multiroom, "update_status", AsyncMock()
    ) as mock_update_status:
        await controller.discover_multirooms()

        # Assert multiroom update_status was called
        mock_update_status.assert_called_once_with(controller.bridges)

        # Assert multiroom is added to the controller
        assert len(controller.multirooms) == 1
        assert controller.multirooms[0] == mock_multiroom


@pytest.mark.asyncio
async def test_discover_multirooms_no_followers(
    controller, mock_bridge, mock_multiroom
):
    """Test discover_multirooms when multirooms have no followers."""
    mock_bridge.multiroom = mock_multiroom
    mock_multiroom.leader = mock_bridge
    mock_multiroom.followers = []

    controller.bridges.append(mock_bridge)

    with patch.object(
        mock_multiroom, "update_status", AsyncMock()
    ) as mock_update_status:
        await controller.discover_multirooms()

        # Assert multiroom update_status was called
        mock_update_status.assert_called_once_with(controller.bridges)

        # Assert multiroom is not added to the controller
        assert len(controller.multirooms) == 0
        assert mock_bridge.multiroom is None


@pytest.mark.asyncio
async def test_discover_multirooms_exception_handling(
    controller, mock_bridge, mock_multiroom
):
    """Test discover_multirooms handles exceptions during multiroom updates."""
    mock_bridge.multiroom = mock_multiroom
    mock_multiroom.leader = mock_bridge
    mock_multiroom.followers = []

    controller.bridges.append(mock_bridge)

    with patch.object(
        mock_multiroom,
        "update_status",
        AsyncMock(side_effect=LinkPlayInvalidDataException),
    ):
        with patch("linkplay.controller.LOGGER.exception") as mock_logger:
            await controller.discover_multirooms()

            # Assert exception was logged
            mock_logger.assert_called_once()

            # Assert multiroom is not added to the controller
            assert len(controller.multirooms) == 0
            assert mock_bridge.multiroom is None


@pytest.mark.asyncio
async def test_discover_multirooms_create_new(controller, mock_bridge):
    """Test discover_multirooms creates a new multiroom from a bridge."""
    mock_bridge.multiroom = None

    controller.bridges.append(mock_bridge)

    mock_new_multiroom = MagicMock(spec=LinkPlayMultiroom)
    mock_new_multiroom.followers = [MagicMock(spec=LinkPlayBridge)]

    with patch(
        "linkplay.controller.LinkPlayMultiroom", return_value=mock_new_multiroom
    ) as mock_multiroom_class:
        with patch.object(mock_new_multiroom, "update_status", AsyncMock()):
            await controller.discover_multirooms()

            # Assert LinkPlayMultiroom was instantiated
            mock_multiroom_class.assert_called_once_with(mock_bridge)

            # Assert multiroom update_status was called
            mock_new_multiroom.update_status.assert_called_once_with(controller.bridges)

            # Assert the new multiroom is added to the controller
            assert len(controller.multirooms) == 1
            assert controller.multirooms[0] == mock_new_multiroom

            # Assert the bridge's multiroom is updated
            assert mock_bridge.multiroom == mock_new_multiroom
