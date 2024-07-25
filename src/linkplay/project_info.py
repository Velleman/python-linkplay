"""Utilities for fetching manufacturer and model from a project."""

from typing import Final
from dataclasses import dataclass

MANUFACTURER_ARTSOUND: Final[str] = "ArtSound"
MANUFACTURER_GENERIC: Final[str] = "Generic"
MODELS_ARTSOUND_SMART_ZONE4: Final[str] = "Smart Zone 4 AMP"
MODELS_ARTSOUND_SMART_HYDE: Final[str] = "Smart Hyde"
MODELS_GENERIC: Final[str] = "Generic"


@dataclass
class ProjectInfo:
    """Dataclass representing project information."""

    manufacturer: str
    model: str


def get_project_info(project: str) -> ProjectInfo:
    """Get ProjectInfo for given project."""
    match project:
        case "SMART_ZONE4_AMP":
            return ProjectInfo(
                manufacturer=MANUFACTURER_ARTSOUND, model=MODELS_ARTSOUND_SMART_ZONE4
            )
        case "SMART_HYDE":
            return ProjectInfo(
                manufacturer=MANUFACTURER_ARTSOUND, model=MODELS_ARTSOUND_SMART_HYDE
            )
        case _:
            return ProjectInfo(manufacturer=MANUFACTURER_GENERIC, model=MODELS_GENERIC)
