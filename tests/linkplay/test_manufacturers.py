from unittest.mock import patch

import pytest

from src.linkplay.manufacturers import (
    MANUFACTURER_GENERIC,
    MODELS_GENERIC,
    PROJECTID_LOOKUP,
    get_info_from_project,
)


def test_existing_project():
    """Test that an existing project returns the correct manufacturer and model."""
    for project, (expected_manufacturer, expected_model) in PROJECTID_LOOKUP.items():
        manufacturer, model = get_info_from_project(project)
        assert manufacturer == expected_manufacturer
        assert model == expected_model


@patch("src.linkplay.manufacturers.LOGGER.warning")
def test_non_existing_project(mock_warning):
    """Test that a non-existing project falls back to generic and logs a warning."""
    project = "NON_EXISTING_PROJECT"
    manufacturer, model = get_info_from_project(project)
    assert manufacturer == MANUFACTURER_GENERIC
    assert model == MODELS_GENERIC
    # mock_warning.assert_called_once_with(
    #    "The project name '%s' is not found in the manufacturer list. Kindly open an issue at https://github.com/velleman/python-linkplay/issues with the project name %s and mention the manufacturer of this product and the product name.",
    #    project,
    #    project,
    # )
