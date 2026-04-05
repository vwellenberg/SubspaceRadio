"""Shared test fixtures for SubspaceRadio."""

import sys
from dataclasses import dataclass, field
from pathlib import Path

import pytest

# Add src to path so we can import swingmusic modules without full install
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


@dataclass
class MockUserConfig:
    """Lightweight UserConfig substitute for testing without filesystem/singleton side effects."""

    artistSeparators: set[str] = field(default_factory=lambda: {";", "/", "&"})
    artistSplitIgnoreList: set[str] = field(default_factory=lambda: {"AC/DC", "Earth, Wind & Fire"})
    genreSeparators: set[str] = field(default_factory=lambda: {"/", ";", "&"})
    extractFeaturedArtists: bool = True
    removeProdBy: bool = True
    removeRemasterInfo: bool = True
    cleanAlbumTitle: bool = True
    mergeAlbums: bool = False
    showAlbumsAsSingles: bool = False


@pytest.fixture
def config():
    return MockUserConfig()


@pytest.fixture
def config_no_ignore():
    return MockUserConfig(artistSplitIgnoreList=set())
