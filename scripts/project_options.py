"""Shared project option helpers for CLI and GUI launchers."""

from __future__ import annotations

PROJECT_TYPE_SURFACES = {
    "website": ["website"],
    "landing": ["landing"],
    "mobile-web-app": ["web", "mobile", "backend"],
    "desktop-python": ["desktop-python"],
    "chrome-extension": ["chrome-extension"],
}
LIMITED_FEATURE_PROJECT_TYPES = {"website", "landing", "desktop-python", "chrome-extension"}
SIMPLE_PROJECT_FEATURES = {"design-starter"}


def surfaces_for_project_type(project_type: str) -> list[str]:
    return list(PROJECT_TYPE_SURFACES.get(project_type, PROJECT_TYPE_SURFACES["mobile-web-app"]))
