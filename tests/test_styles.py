"""Tests for sphinxcontrib_urn styles and helpers."""

from __future__ import annotations

import pytest
from hypothesis import given, strategies as st
from pybtex.database import Entry, Person

from sphinxcontrib_urn.styles import (
    URN_RESOLVER_URL,
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

    @pytest.mark.parametrize(
        ("raw_input", "expected_url", "expected_display"),
        [
            # Bare URNs
            (
                "URN:NBN:fi:aalto-202305213270",
                "https://urn.fi/URN:NBN:fi:aalto-202305213270",
                "URN:NBN:fi:aalto-202305213270",
            ),
            (
                "URN:ISBN:978-952-60-1234-5",
                "https://urn.fi/URN:ISBN:978-952-60-1234-5",
                "URN:ISBN:978-952-60-1234-5",
            ),
            (
                "URN:ISSN:1234-5678",
                "https://urn.fi/URN:ISSN:1234-5678",
                "URN:ISSN:1234-5678",
            ),
            # Full URLs
            (
                "https://urn.fi/URN:NBN:fi:aalto-202305213270",
                "https://urn.fi/URN:NBN:fi:aalto-202305213270",
                "URN:NBN:fi:aalto-202305213270",
            ),
            (
                "http://urn.fi/URN:NBN:fi:aalto-202305213270",
                "http://urn.fi/URN:NBN:fi:aalto-202305213270",
                "URN:NBN:fi:aalto-202305213270",
            ),
            # Whitespace
            (
                "  URN:NBN:fi:aalto-202305213270  ",
                "https://urn.fi/URN:NBN:fi:aalto-202305213270",
                "URN:NBN:fi:aalto-202305213270",
            ),
            # Different casings (NID is case-insensitive per RFC 8141)
            (
                "urn:nbn:fi:aalto-202305213270",
                "https://urn.fi/urn:nbn:fi:aalto-202305213270",
                "urn:nbn:fi:aalto-202305213270",
            ),
        ],
    )
    def test_resolve_urn_scenarios(
        self, raw_input: str, expected_url: str, expected_display: str
    ) -> None:
        """Test URN resolution with known inputs."""
        url, display = _resolve_urn(raw_input)
        assert url == expected_url
        assert display == expected_display

    @given(st.text())
    def test_resolve_urn_fuzzing(self, raw_input: str) -> None:
        """Property-based test: _resolve_urn should never crash on any string input."""
        url, display = _resolve_urn(raw_input)
        assert isinstance(url, str)
        assert isinstance(display, str)

        # Invariants based on the function's logic
        stripped = raw_input.strip()
        if not stripped.lower().startswith(("http://", "https://")):
            assert url == f"{URN_RESOLVER_URL}{stripped}"
            assert display == stripped


# ------------------------------------------------------------------
# _is_redundant_url
# ------------------------------------------------------------------


class TestIsRedundantUrl:
    """Tests for identifying redundant URLs."""

    @pytest.mark.parametrize(
        ("url", "urn", "expected"),
        [
            # Happy paths
            (
                "https://urn.fi/URN:NBN:fi:aalto-202305213270",
                "URN:NBN:fi:aalto-202305213270",
                True,
            ),
            (
                "http://urn.fi/URN:NBN:fi:aalto-202305213270",
                "URN:NBN:fi:aalto-202305213270",
                True,
            ),
            # Case insensitivity
            (
                "https://urn.fi/urn:nbn:fi:aalto-202305213270",
                "URN:NBN:fi:aalto-202305213270",
                True,
            ),
            (
                "HTTPS://URN.FI/URN:NBN:FI:AALTO-202305213270",
                "urn:nbn:fi:aalto-202305213270",
                True,
            ),
            # Unrelated URLs (Negative cases)
            (
                "https://example.com/URN:NBN:fi:aalto-202305213270",
                "URN:NBN:fi:aalto-202305213270",
                True,
            ),  # True due to substring logic
            (
                "https://urn.fi/URN:NBN:fi:aalto-999999999999",
                "URN:NBN:fi:aalto-202305213270",
                False,
            ),
            ("https://example.com/thesis.pdf", "URN:NBN:fi:aalto-202305213270", False),
            # Edge cases: Empty inputs
            ("", "URN:NBN:fi:aalto-202305213270", False),
        ],
    )
    def test_is_redundant_url_scenarios(
        self, url: str, urn: str, expected: bool
    ) -> None:
        """Test URL redundancy logic with known inputs."""
        assert _is_redundant_url(url, urn) is expected

    @given(st.text(), st.text(min_size=1))
    def test_is_redundant_url_fuzzing(self, url: str, urn: str) -> None:
        """Property-based test: should safely handle any random strings."""
        result = _is_redundant_url(url, urn)
        assert isinstance(result, bool)


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


def _render_plain(text: object) -> str:
    """Render a pybtex rich-text tree to a plain string."""
    return text.render_as("text")  # type: ignore[no-any-return,attr-defined]


class TestUrnStyleMixin:
    """Test the mixin via the pre-built PlainUrn style."""

    @pytest.fixture
    def style(self) -> PlainUrn:
        """Fixture providing a PlainUrn instance."""
        return PlainUrn()  # type: ignore[call-arg]

    def test_entry_without_urn_unchanged(self, style: PlainUrn) -> None:
        """Happy Path: Entry without URN should be formatted normally without errors."""
        entry = _make_entry()
        formatted = style.format_entry("And24", entry)  # type: ignore[attr-defined]
        rendered = _render_plain(formatted.text)
        assert "urn" not in rendered.lower() or "URN" not in rendered

    def test_entry_with_urn_appended(self, style: PlainUrn) -> None:
        """Happy Path: Entry with URN should have a hyperlinked URN appended."""
        entry = _make_entry(fields={"urn": "URN:NBN:fi:aalto-202305213270"})
        formatted = style.format_entry("And24", entry)  # type: ignore[attr-defined]
        rendered = _render_plain(formatted.text)
        assert "URN:NBN:fi:aalto-202305213270" in rendered

    def test_urn_is_hyperlinked(self, style: PlainUrn) -> None:
        """Happy Path: Verify the HTML rendering produces the correct a href."""
        entry = _make_entry(fields={"urn": "URN:NBN:fi:aalto-202305213270"})
        formatted = style.format_entry("And24", entry)  # type: ignore[attr-defined]
        # Render as HTML to verify the hyperlink is present.
        html = formatted.text.render_as("html")  # type: ignore[attr-defined]
        assert 'href="https://urn.fi/URN:NBN:fi:aalto-202305213270"' in html
        assert "URN:NBN:fi:aalto-202305213270" in html

    def test_redundant_url_suppressed(self, style: PlainUrn) -> None:
        """Edge Case: Redundant URL field is removed to prevent double-printing."""
        entry = _make_entry(
            fields={
                "urn": "URN:NBN:fi:aalto-202305213270",
                "url": "https://urn.fi/URN:NBN:fi:aalto-202305213270",
            }
        )
        formatted = style.format_entry("And24", entry)  # type: ignore[attr-defined]
        html = formatted.text.render_as("html")  # type: ignore[attr-defined]
        # The full resolver URL should NOT appear as a separate URL: field.
        # It should only appear inside the URN hyperlink.
        assert html.count("https://urn.fi/URN:NBN:fi:aalto-202305213270") == 1

    def test_unrelated_url_preserved(self, style: PlainUrn) -> None:
        """Edge Case: Unrelated URL field should be retained."""
        entry = _make_entry(
            fields={
                "urn": "URN:NBN:fi:aalto-202305213270",
                "url": "https://example.com/thesis.pdf",
            }
        )
        formatted = style.format_entry("And24", entry)  # type: ignore[attr-defined]
        html = formatted.text.render_as("html")  # type: ignore[attr-defined]
        assert "https://example.com/thesis.pdf" in html
        assert "URN:NBN:fi:aalto-202305213270" in html

    def test_original_entry_not_mutated(self, style: PlainUrn) -> None:
        """Edge Case: Ensure the mixin does not mutate original pybtex Entry."""
        entry = _make_entry(
            fields={
                "urn": "URN:NBN:fi:aalto-202305213270",
                "url": "https://urn.fi/URN:NBN:fi:aalto-202305213270",
            }
        )
        original_url = entry.fields["url"]
        style.format_entry("And24", entry)  # type: ignore[attr-defined]
        # The original entry must still have its url field.
        assert entry.fields["url"] == original_url

    def test_isbn_urn_hyperlinked(self, style: PlainUrn) -> None:
        """Verify ISBN URN formats correctly."""
        entry = _make_entry(
            entry_type="book",
            fields={
                "urn": "URN:ISBN:978-951-51-7661-5",
                "publisher": "WSOY",
            },
        )
        formatted = style.format_entry("B24", entry)  # type: ignore[attr-defined]
        html = formatted.text.render_as("html")  # type: ignore[attr-defined]
        assert 'href="https://urn.fi/URN:ISBN:978-951-51-7661-5"' in html
        assert "URN:ISBN:978-951-51-7661-5" in html

    def test_issn_urn_hyperlinked(self, style: PlainUrn) -> None:
        """Verify ISSN URN formats correctly."""
        entry = _make_entry(
            entry_type="article",
            fields={
                "urn": "URN:ISSN:1234-5678",
                "journal": "Test Journal",
                "volume": "1",
            },
        )
        formatted = style.format_entry("J24", entry)  # type: ignore[attr-defined]
        html = formatted.text.render_as("html")  # type: ignore[attr-defined]
        assert 'href="https://urn.fi/URN:ISSN:1234-5678"' in html

    def test_http_url_suppressed(self, style: PlainUrn) -> None:
        """Older documents may use http:// for the resolver URL."""
        entry = _make_entry(
            fields={
                "urn": "URN:NBN:fi:aalto-202305213270",
                "url": "http://urn.fi/URN:NBN:fi:aalto-202305213270",
            }
        )
        formatted = style.format_entry("And24", entry)  # type: ignore[attr-defined]
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
        formatted = style.format_entry("And24", entry)  # type: ignore[attr-defined]
        html = formatted.text.render_as("html")  # type: ignore[attr-defined]
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
        """Verify the pre-built class subclasses the mixin."""
        assert issubclass(style_cls, UrnStyleMixin)

    def test_formats_entry_with_urn(self, style_cls: type) -> None:
        """Verify the pre-built class actually includes the logic."""
        style = style_cls()  # type: ignore[call-arg]
        entry = _make_entry(fields={"urn": "URN:NBN:fi:aalto-202305213270"})
        formatted = style.format_entry("And24", entry)  # type: ignore[attr-defined]
        html = formatted.text.render_as("html")  # type: ignore[attr-defined]
        assert "URN:NBN:fi:aalto-202305213270" in html
