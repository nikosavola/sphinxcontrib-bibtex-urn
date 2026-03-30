"""Tests for sphinxcontrib_urn styles and helpers."""

from __future__ import annotations

import pytest
from pybtex.database import Entry, Person

from sphinxcontrib_urn.styles import (
    AlphaUrn,
    PlainUrn,
    UnsrtAlphaUrn,
    UnsrtUrn,
    UrnStyleMixin,
    _is_redundant_url,
    _resolve_urn,
)

# ------------------------------------------------------------------
# _resolve_urn
# ------------------------------------------------------------------


class TestResolveUrn:
    """Tests for the URN resolver helper."""

    def test_bare_identifier(self) -> None:
        url, display = _resolve_urn("URN:NBN:fi:aalto-202305213270")
        assert url == "https://urn.fi/URN:NBN:fi:aalto-202305213270"
        assert display == "URN:NBN:fi:aalto-202305213270"

    def test_full_https_url(self) -> None:
        url, display = _resolve_urn("https://urn.fi/URN:NBN:fi:aalto-202305213270")
        assert url == "https://urn.fi/URN:NBN:fi:aalto-202305213270"
        assert display == "URN:NBN:fi:aalto-202305213270"

    def test_full_http_url(self) -> None:
        url, display = _resolve_urn("http://urn.fi/URN:NBN:fi:aalto-202305213270")
        assert url == "http://urn.fi/URN:NBN:fi:aalto-202305213270"
        assert display == "URN:NBN:fi:aalto-202305213270"

    def test_whitespace_stripped(self) -> None:
        url, display = _resolve_urn("  URN:NBN:fi:aalto-202305213270  ")
        assert url == "https://urn.fi/URN:NBN:fi:aalto-202305213270"
        assert display == "URN:NBN:fi:aalto-202305213270"

    def test_isbn_urn(self) -> None:
        url, display = _resolve_urn("URN:ISBN:978-952-60-1234-5")
        assert url == "https://urn.fi/URN:ISBN:978-952-60-1234-5"
        assert display == "URN:ISBN:978-952-60-1234-5"

    def test_issn_urn(self) -> None:
        url, display = _resolve_urn("URN:ISSN:1234-5678")
        assert url == "https://urn.fi/URN:ISSN:1234-5678"
        assert display == "URN:ISSN:1234-5678"

    def test_lowercase_urn(self) -> None:
        """NID is case-insensitive per RFC 8141."""
        url, display = _resolve_urn("urn:nbn:fi:aalto-202305213270")
        assert url == "https://urn.fi/urn:nbn:fi:aalto-202305213270"
        assert display == "urn:nbn:fi:aalto-202305213270"


# ------------------------------------------------------------------
# _is_redundant_url
# ------------------------------------------------------------------


class TestIsRedundantUrl:
    """Tests for identifying redundant URLs."""

    def test_exact_https_match(self) -> None:
        assert _is_redundant_url(
            "https://urn.fi/URN:NBN:fi:aalto-202305213270",
            "URN:NBN:fi:aalto-202305213270",
        )

    def test_exact_http_match(self) -> None:
        assert _is_redundant_url(
            "http://urn.fi/URN:NBN:fi:aalto-202305213270",
            "URN:NBN:fi:aalto-202305213270",
        )

    def test_case_insensitive_nid(self) -> None:
        """URL uses lowercase urn:nbn:fi, bibtex uses uppercase URN:NBN:fi."""
        assert _is_redundant_url(
            "https://urn.fi/urn:nbn:fi:aalto-202305213270",
            "URN:NBN:fi:aalto-202305213270",
        )

    def test_isbn_url(self) -> None:
        assert _is_redundant_url(
            "https://urn.fi/URN:ISBN:978-951-51-7661-5",
            "URN:ISBN:978-951-51-7661-5",
        )

    def test_unrelated_url(self) -> None:
        assert not _is_redundant_url(
            "https://example.com/thesis.pdf",
            "URN:NBN:fi:aalto-202305213270",
        )

    def test_different_urn_in_url(self) -> None:
        assert not _is_redundant_url(
            "https://urn.fi/URN:NBN:fi:aalto-999999999999",
            "URN:NBN:fi:aalto-202305213270",
        )


# ------------------------------------------------------------------
# UrnStyleMixin.format_entry
# ------------------------------------------------------------------


def _make_entry(
    entry_type: str = "mastersthesis",
    fields: dict[str, str] | None = None,
) -> Entry:
    """Create a minimal pybtex Entry for testing."""
    default_fields = {
        "title": "Test Thesis",
        "school": "Aalto University",
        "year": "2024",
    }
    if fields:
        default_fields.update(fields)
    entry = Entry(entry_type, fields=default_fields)
    entry.persons["author"] = [Person("Andersson, Joona")]
    return entry


def _render_plain(text) -> str:
    """Render a pybtex rich-text tree to a plain string."""
    return text.render_as("text")


class TestUrnStyleMixin:
    """Test the mixin via the pre-built PlainUrn style."""

    @pytest.fixture
    def style(self) -> PlainUrn:
        """Fixture providing a PlainUrn instance."""
        return PlainUrn()

    def test_entry_without_urn_unchanged(self, style: PlainUrn) -> None:
        entry = _make_entry()
        formatted = style.format_entry("And24", entry)
        rendered = _render_plain(formatted.text)
        assert "urn" not in rendered.lower() or "URN" not in rendered

    def test_entry_with_urn_appended(self, style: PlainUrn) -> None:
        entry = _make_entry(fields={"urn": "URN:NBN:fi:aalto-202305213270"})
        formatted = style.format_entry("And24", entry)
        rendered = _render_plain(formatted.text)
        assert "URN:NBN:fi:aalto-202305213270" in rendered

    def test_urn_is_hyperlinked(self, style: PlainUrn) -> None:
        entry = _make_entry(fields={"urn": "URN:NBN:fi:aalto-202305213270"})
        formatted = style.format_entry("And24", entry)
        # Render as HTML to verify the hyperlink is present.
        html = formatted.text.render_as("html")
        assert 'href="https://urn.fi/URN:NBN:fi:aalto-202305213270"' in html
        assert "URN:NBN:fi:aalto-202305213270" in html

    def test_redundant_url_suppressed(self, style: PlainUrn) -> None:
        entry = _make_entry(
            fields={
                "urn": "URN:NBN:fi:aalto-202305213270",
                "url": "https://urn.fi/URN:NBN:fi:aalto-202305213270",
            }
        )
        formatted = style.format_entry("And24", entry)
        html = formatted.text.render_as("html")
        # The full resolver URL should NOT appear as a separate URL: field.
        # It should only appear inside the URN hyperlink.
        assert html.count("https://urn.fi/URN:NBN:fi:aalto-202305213270") == 1

    def test_unrelated_url_preserved(self, style: PlainUrn) -> None:
        entry = _make_entry(
            fields={
                "urn": "URN:NBN:fi:aalto-202305213270",
                "url": "https://example.com/thesis.pdf",
            }
        )
        formatted = style.format_entry("And24", entry)
        html = formatted.text.render_as("html")
        assert "https://example.com/thesis.pdf" in html
        assert "URN:NBN:fi:aalto-202305213270" in html

    def test_original_entry_not_mutated(self, style: PlainUrn) -> None:
        entry = _make_entry(
            fields={
                "urn": "URN:NBN:fi:aalto-202305213270",
                "url": "https://urn.fi/URN:NBN:fi:aalto-202305213270",
            }
        )
        original_url = entry.fields["url"]
        style.format_entry("And24", entry)
        # The original entry must still have its url field.
        assert entry.fields["url"] == original_url

    def test_isbn_urn_hyperlinked(self, style: PlainUrn) -> None:
        entry = _make_entry(
            entry_type="book",
            fields={
                "urn": "URN:ISBN:978-951-51-7661-5",
                "publisher": "WSOY",
            },
        )
        formatted = style.format_entry("B24", entry)
        html = formatted.text.render_as("html")
        assert 'href="https://urn.fi/URN:ISBN:978-951-51-7661-5"' in html
        assert "URN:ISBN:978-951-51-7661-5" in html

    def test_issn_urn_hyperlinked(self, style: PlainUrn) -> None:
        entry = _make_entry(
            entry_type="article",
            fields={
                "urn": "URN:ISSN:1234-5678",
                "journal": "Test Journal",
                "volume": "1",
            },
        )
        formatted = style.format_entry("J24", entry)
        html = formatted.text.render_as("html")
        assert 'href="https://urn.fi/URN:ISSN:1234-5678"' in html

    def test_http_url_suppressed(self, style: PlainUrn) -> None:
        """Older documents may use http:// for the resolver URL."""
        entry = _make_entry(
            fields={
                "urn": "URN:NBN:fi:aalto-202305213270",
                "url": "http://urn.fi/URN:NBN:fi:aalto-202305213270",
            }
        )
        formatted = style.format_entry("And24", entry)
        rendered = _render_plain(formatted.text)
        # http URL must be gone; only the urn.fi hyperlink remains.
        assert rendered.count("urn.fi") == 0  # plain text has no href
        assert "URN:NBN:fi:aalto-202305213270" in rendered

    def test_case_insensitive_url_suppressed(self, style: PlainUrn) -> None:
        """URL may use different casing for the URN prefix per RFC 8141."""
        entry = _make_entry(
            fields={
                "urn": "URN:NBN:fi:aalto-202305213270",
                "url": "https://urn.fi/urn:nbn:fi:aalto-202305213270",
            }
        )
        formatted = style.format_entry("And24", entry)
        html = formatted.text.render_as("html")
        # Only one hyperlink should appear (the URN one).
        assert html.count("urn.fi") == 1


# ------------------------------------------------------------------
# Pre-built styles are valid pybtex styles
# ------------------------------------------------------------------


@pytest.mark.parametrize(
    "style_cls",
    [PlainUrn, UnsrtUrn, AlphaUrn, UnsrtAlphaUrn],
    ids=["plain", "unsrt", "alpha", "unsrtalpha"],
)
class TestPrebuiltStyles:
    """Tests for pre-built style classes."""

    def test_is_urn_aware(self, style_cls: type) -> None:
        assert issubclass(style_cls, UrnStyleMixin)

    def test_formats_entry_with_urn(self, style_cls: type) -> None:
        style = style_cls()
        entry = _make_entry(fields={"urn": "URN:NBN:fi:aalto-202305213270"})
        formatted = style.format_entry("And24", entry)
        html = formatted.text.render_as("html")
        assert "URN:NBN:fi:aalto-202305213270" in html
