"""Tests for playlist track reordering logic."""

import sys
from unittest.mock import MagicMock, patch

# Mock heavy dependencies before importing swingmusic modules
for mod_name in [
    "flask_jwt_extended",
    "flask",
    "flask_cors",
    "flask_compress",
    "flask_openapi3",
    "PIL",
    "colorgram",
    "tqdm",
    "tinytag",
    "psutil",
    "show_in_file_manager",
    "tabulate",
    "setproctitle",
    "watchdog",
    "sqlalchemy",
    "sortedcontainers",
    "ffmpeg",
    "schedule",
    "pystray",
    "rapidfuzz",
]:
    if mod_name not in sys.modules:
        sys.modules[mod_name] = MagicMock()


class TestReorderTracksEndpoint:
    """Tests for the reorder_playlist_tracks API endpoint logic."""

    def _make_playlist(self, trackhashes: list[str]):
        playlist = MagicMock()
        playlist.trackhashes = trackhashes
        return playlist

    def test_reorder_returns_404_when_playlist_not_found(self):
        with patch("swingmusic.db.userdata.PlaylistTable.get_by_id", return_value=None):
            from swingmusic.api.playlist import reorder_playlist_tracks

            path = MagicMock()
            path.playlistid = "999"
            body = MagicMock()
            body.trackhashes = ["a", "b", "c"]

            result, status = reorder_playlist_tracks(path, body)

            assert status == 404
            assert "error" in result

    def test_reorder_returns_200_on_success(self):
        playlist = self._make_playlist(["a", "b", "c"])

        with (
            patch("swingmusic.db.userdata.PlaylistTable.get_by_id", return_value=playlist),
            patch("swingmusic.db.userdata.PlaylistTable.update_one") as mock_update,
        ):
            from swingmusic.api.playlist import reorder_playlist_tracks

            path = MagicMock()
            path.playlistid = "1"
            body = MagicMock()
            body.trackhashes = ["c", "a", "b"]

            result, status = reorder_playlist_tracks(path, body)

            assert status == 200
            mock_update.assert_called_once_with(1, {"trackhashes": ["c", "a", "b"]})

    def test_reorder_persists_new_order(self):
        original = ["hash1", "hash2", "hash3", "hash4"]
        playlist = self._make_playlist(original)
        captured = {}

        def capture_update(pid, data):
            captured["trackhashes"] = data["trackhashes"]

        with (
            patch("swingmusic.db.userdata.PlaylistTable.get_by_id", return_value=playlist),
            patch("swingmusic.db.userdata.PlaylistTable.update_one", side_effect=capture_update),
        ):
            from swingmusic.api.playlist import reorder_playlist_tracks

            path = MagicMock()
            path.playlistid = "1"
            body = MagicMock()
            body.trackhashes = ["hash4", "hash1", "hash3", "hash2"]

            reorder_playlist_tracks(path, body)

            assert captured["trackhashes"] == ["hash4", "hash1", "hash3", "hash2"]


class TestMoveTrackLogic:
    """Tests for the moveTrack array manipulation logic (mirrors frontend store logic)."""

    @staticmethod
    def move_track(tracks: list, from_idx: int, to_idx: int) -> list:
        """Python equivalent of the TypeScript moveTrack store action."""
        result = tracks[:]
        item = result.pop(from_idx)
        adjusted = to_idx - 1 if to_idx > from_idx else to_idx
        result.insert(adjusted, item)
        return result

    def test_move_forward(self):
        tracks = ["a", "b", "c", "d", "e"]
        result = self.move_track(tracks, 0, 3)
        assert result == ["b", "c", "a", "d", "e"]

    def test_move_backward(self):
        tracks = ["a", "b", "c", "d", "e"]
        result = self.move_track(tracks, 3, 1)
        assert result == ["a", "d", "b", "c", "e"]

    def test_move_to_end(self):
        tracks = ["a", "b", "c"]
        result = self.move_track(tracks, 0, 3)
        assert result == ["b", "c", "a"]

    def test_move_to_beginning(self):
        tracks = ["a", "b", "c"]
        result = self.move_track(tracks, 2, 0)
        assert result == ["c", "a", "b"]

    def test_move_adjacent_forward_is_noop(self):
        tracks = ["a", "b", "c"]
        # dropping on bottom half of same item or top half of next → no move
        result = self.move_track(tracks, 1, 2)
        assert result == ["a", "b", "c"]

    def test_original_unchanged(self):
        tracks = ["a", "b", "c"]
        self.move_track(tracks, 0, 2)
        assert tracks == ["a", "b", "c"]
