"""Tests for the Sphinx extension setup and auto-patching."""

from __future__ import annotations

import logging
from unittest.mock import MagicMock, patch

import pytest

from sphinxcontrib_urn import UrnStyleMixin, _patch_style, setup


# A dummy class that looks like a Pybtex style for testing.
class MockBaseStyle:
    """A mock pybtex style base class."""


# A dummy class that is already URN-aware.
class MockAlreadyUrnStyle(UrnStyleMixin, MockBaseStyle):
    """A mock pybtex style that already includes the mixin."""


class TestPatchStyle:
    """Tests for the _patch_style function."""

    @patch("sphinxcontrib_urn.find_plugin")
    @patch("sphinxcontrib_urn.register_plugin")
    def test_patch_style_success(
        self, mock_register: MagicMock, mock_find: MagicMock
    ) -> None:
        """Happy Path: Wraps an existing style successfully."""
        mock_find.return_value = MockBaseStyle
        app = MagicMock()
        app.config.bibtex_default_style = "unsrt"

        _patch_style(app)

        mock_find.assert_called_once_with("pybtex.style.formatting", "unsrt")
        mock_register.assert_called_once()
        args, _ = mock_register.call_args

        assert args[0] == "pybtex.style.formatting"
        assert args[1] == "_urn_wrapped_unsrt"
        # Verify the new style class is a subclass of UrnStyleMixin and the base class
        new_style_cls = args[2]
        assert issubclass(new_style_cls, UrnStyleMixin)
        assert issubclass(new_style_cls, MockBaseStyle)

        assert app.config.bibtex_default_style == "_urn_wrapped_unsrt"

    @patch("sphinxcontrib_urn.find_plugin")
    @patch("sphinxcontrib_urn.register_plugin")
    def test_patch_style_already_urn_aware(
        self, mock_register: MagicMock, mock_find: MagicMock
    ) -> None:
        """Edge Case: Does nothing if the style is already URN-aware."""
        mock_find.return_value = MockAlreadyUrnStyle
        app = MagicMock()
        app.config.bibtex_default_style = "urn_plain"

        _patch_style(app)

        mock_find.assert_called_once_with("pybtex.style.formatting", "urn_plain")
        mock_register.assert_not_called()
        assert app.config.bibtex_default_style == "urn_plain"

    @patch("sphinxcontrib_urn.find_plugin")
    @patch("sphinxcontrib_urn.register_plugin")
    def test_patch_style_not_found(
        self,
        mock_register: MagicMock,
        mock_find: MagicMock,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """Error Handling: Logs a warning and returns early if style is missing."""
        mock_find.side_effect = Exception("Plugin not found")
        app = MagicMock()
        app.config.bibtex_default_style = "nonexistent"

        with caplog.at_level(logging.WARNING):
            _patch_style(app)

        mock_find.assert_called_once_with("pybtex.style.formatting", "nonexistent")
        mock_register.assert_not_called()
        assert app.config.bibtex_default_style == "nonexistent"
        assert "could not find pybtex style 'nonexistent'" in caplog.text


class TestSetup:
    """Tests for the extension setup function."""

    def test_setup_returns_metadata(self) -> None:
        """Happy Path: Setup connects the listener and returns correct metadata."""
        app = MagicMock()
        result = setup(app)

        assert "version" in result
        assert result["parallel_read_safe"] is True
        assert result["parallel_write_safe"] is True
        app.connect.assert_called_once_with("builder-inited", _patch_style)
