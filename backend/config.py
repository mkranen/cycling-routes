"""
Configuration module for the application.
Contains global variables and settings.
"""

import os
from pathlib import Path

# Define root directory and download directory
ROOT_DIR = Path(__file__).parent.parent
DOWNLOAD_DIR = ROOT_DIR / "downloads"

# Default sources for Komoot routes
DEFAULT_SOURCES = [
    "personal",
    "gravelritten",
    "gijs_bruinsma",
]


# Ensure download directory exists
def ensure_download_dir(source: str = None) -> Path:
    """Ensure download directory exists and return Path object"""
    if source:
        source_dir = DOWNLOAD_DIR / source
        source_dir.mkdir(parents=True, exist_ok=True)
        return source_dir
    else:
        DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
        return DOWNLOAD_DIR


# Ensure gpx download directory exists
def ensure_gpx_download_dir(collection_slug: str, activity_type: str) -> Path:
    """Ensure gpx download directory exists and return Path object"""

    if collection_slug and activity_type:
        source_dir = DOWNLOAD_DIR / collection_slug / activity_type
        source_dir.mkdir(parents=True, exist_ok=True)
        return source_dir
    else:
        DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
        return DOWNLOAD_DIR
