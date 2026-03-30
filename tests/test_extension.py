"""Tests for the Sphinx extension setup and auto-patching."""

from __future__ import annotations

from unittest.mock import MagicMock

from sphinxcontrib_urn import _patch_style, setup


class TestSetup:
    """Tests for the extension setup function."""

    def test_setup_returns_metadata(self) -> None:
        app = MagicMock()
        result = setup(app)
        assert "version" in result
        assert result["parallel_read_safe"] is True
        assert result["parallel_write_safe"] is True
        app.connect.assert_called_once_with("builder-inited", _patch_style)
