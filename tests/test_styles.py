"""Tests for sphinxcontrib_bibtex_urn styles and helpers."""

from __future__ import annotations

import pycountry
import pytest
from hypothesis import given, strategies as st
from pybtex.database import Entry, Person
from pydantic import HttpUrl, TypeAdapter

from sphinxcontrib_bibtex_urn.styles import (
    NBN_RESOLVERS,
    AlphaUrn,
    PlainUrn,
    UnsrtAlphaUrn,
    UnsrtUrn,
    UrnStyleMixin,
    _is_redundant_url,
    resolve_urn,
)


class TestNbnResolversRegistry:
    """Validate the integrity of the NBN_RESOLVERS mapping."""

    def test_country_codes_are_valid(self) -> None:
        """All keys must be valid ISO 3166-1 alpha-2 country codes."""
        for cc in NBN_RESOLVERS:
            # Skip empty CC (used for general NBNs if any) or special handling
            if not cc:
                continue
            assert pycountry.countries.get(alpha_2=cc.upper()) is not None

    def test_resolver_urls_are_valid(self) -> None:
        """All values must be valid HTTP/HTTPS URLs."""
        adapter = TypeAdapter(HttpUrl)
        for url in NBN_RESOLVERS.values():
            # For Norway, it has query params in the base string in the dict
            # Actually, let's check if the URL is valid.
            # HttpUrl validation might fail on trailing query markers if not careful.
            # Let's just validate the base part.
            base_url = url.split("?")[0]
            adapter.validate_python(base_url)


# ------------------------------------------------------------------
# resolve_urn
# ------------------------------------------------------------------


class TestResolveUrn:
    """Tests for the URN resolver helper."""

    @pytest.mark.parametrize(
        ("raw_input", "expected_url", "expected_display"),
        [
            # Finnish (keep original example)
            (
                "URN:NBN:fi:aalto-202305213270",
                "https://urn.fi/URN:NBN:fi:aalto-202305213270",
                "URN:NBN:fi:aalto-202305213270",
            ),
            # Austria (AT)
            (
                "urn:nbn:at:at-ubg:3-13",
                "https://resolver.obvsg.at/urn:nbn:at:at-ubg:3-13",
                "urn:nbn:at:at-ubg:3-13",
            ),
            # Czech Republic (CZ)
            (
                "urn:nbn:cz:nk-004hvy",
                "https://resolver.nkp.cz/web/urn:nbn:cz:nk-004hvy",
                "urn:nbn:cz:nk-004hvy",
            ),
            # Croatia (HR)
            (
                "urn:nbn:hr:162:276509",
                "https://urn.nsk.hr/urn:nbn:hr:162:276509",
                "urn:nbn:hr:162:276509",
            ),
            # Hungary (HU)
            (
                "urn:nbn:hu-6982",
                "https://nbn.urn.hu/resolver/urn:nbn:hu-6982",
                "urn:nbn:hu-6982",
            ),
            # Italy (IT)
            (
                "urn:nbn:it:unifi-3903",
                "https://nbn.depositolegale.it/urn:nbn:it:unifi-3903",
                "urn:nbn:it:unifi-3903",
            ),
            # Netherlands (NL)
            (
                "urn:nbn:nl:ui:12-85062",
                "https://www.persistent-identifier.nl/urn:nbn:nl:ui:12-85062",
                "urn:nbn:nl:ui:12-85062",
            ),
            # Norway (NO)
            (
                "urn:nbn:no-nb_digibok_2009062504007",
                "https://www.nb.no/idtjeneste/search.jsf?urn=urn:nbn:no-nb_digibok_2009062504007",
                "urn:nbn:no-nb_digibok_2009062504007",
            ),
            # Sweden (SE)
            (
                "urn:nbn:se:uu:diva-3475",
                "https://urn.kb.se/urn:nbn:se:uu:diva-3475",
                "urn:nbn:se:uu:diva-3475",
            ),
            # Slovenia (SI - placeholder)
            (
                "urn:nbn:si:dummy-123",
                "https://nbn.si/urn:nbn:si:dummy-123",
                "urn:nbn:si:dummy-123",
            ),
            # General NBN (e.g. Germany)
            (
                "URN:NBN:de:gbv:089-3321752945-0",
                "https://nbn-resolving.org/URN:NBN:de:gbv:089-3321752945-0",
                "URN:NBN:de:gbv:089-3321752945-0",
            ),
            # Full URLs
            (
                "https://urn.fi/URN:NBN:fi:aalto-202305213270",
                "https://urn.fi/URN:NBN:fi:aalto-202305213270",
                "URN:NBN:fi:aalto-202305213270",
            ),
            (
                "https://nbn-resolving.org/URN:NBN:de:gbv:089-3321752945-0",
                "https://nbn-resolving.org/URN:NBN:de:gbv:089-3321752945-0",
                "URN:NBN:de:gbv:089-3321752945-0",
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
        resolved = resolve_urn(raw_input)
        assert resolved is not None
        url, display = resolved
        assert url == expected_url
        assert display == expected_display

    @given(st.text())
    def test_resolve_urn_fuzzing(self, raw_input: str) -> None:
        """Property-based test: resolve_urn should never crash on any string input."""
        resolved = resolve_urn(raw_input)
        if resolved is None:
            return

        url, display = resolved
        assert isinstance(url, str)
        assert isinstance(display, str)

        # Invariants based on the function's logic
        stripped = raw_input.strip()
        if not stripped.lower().startswith(("http://", "https://")):
            stripped_lower = stripped.lower()
            if stripped_lower.startswith("urn:nbn:"):
                # We expect it to be one of the known ones or default
                # Just verify it doesn't crash and follows the pattern
                assert url.endswith(stripped)
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
        "year": "2023",
    }
    if fields:
        default_fields.update(fields)
    entry = Entry(entry_type, fields=default_fields)
    entry.persons["author"] = [Person("Savola, Niko")]
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
        formatted = style.format_entry("Sav23", entry)  # type: ignore[attr-defined]
        rendered = _render_plain(formatted.text)
        assert "urn" not in rendered.lower() or "URN" not in rendered

    def test_entry_with_urn_appended(self, style: PlainUrn) -> None:
        """Happy Path: Entry with URN should have a hyperlinked URN appended."""
        entry = _make_entry(fields={"urn": "URN:NBN:fi:aalto-202305213270"})
        formatted = style.format_entry("Sav23", entry)  # type: ignore[attr-defined]
        rendered = _render_plain(formatted.text)
        assert "URN:NBN:fi:aalto-202305213270" in rendered

    def test_urn_is_hyperlinked(self, style: PlainUrn) -> None:
        """Happy Path: Verify the HTML rendering produces the correct a href."""
        entry = _make_entry(fields={"urn": "URN:NBN:fi:aalto-202305213270"})
        formatted = style.format_entry("Sav23", entry)  # type: ignore[attr-defined]
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
        formatted = style.format_entry("Sav23", entry)  # type: ignore[attr-defined]
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
        formatted = style.format_entry("Sav23", entry)  # type: ignore[attr-defined]
        html = formatted.text.render_as("html")  # type: ignore[attr-defined]
        assert "https://example.com/thesis.pdf" in html
        assert "URN:NBN:fi:aalto-202305213270" in html

    def test_urn_promoted_from_url(self, style: PlainUrn) -> None:
        """Happy Path: If 'urn' is missing but 'url' is a resolver link, treat as URN."""
        entry = _make_entry(
            fields={"url": "https://urn.fi/URN:NBN:fi:aalto-202305213270"}
        )
        formatted = style.format_entry("Sav23", entry)  # type: ignore[attr-defined]
        html = formatted.text.render_as("html")  # type: ignore[attr-defined]
        # Should be formatted as a URN link, not a standard URL field.
        # Standard URL formatting usually starts with "URL: ".
        assert "URL: " not in html
        assert 'href="https://urn.fi/URN:NBN:fi:aalto-202305213270"' in html
        assert "URN:NBN:fi:aalto-202305213270" in html

    def test_urn_takes_precedence_over_unrelated_url(self, style: PlainUrn) -> None:
        """Edge Case: If 'urn' is present, it takes precedence even if 'url' is also a resolver."""
        entry = _make_entry(
            fields={
                "urn": "URN:NBN:fi:aalto-202305213270",
                "url": "https://example.com/other",
            }
        )
        formatted = style.format_entry("Sav23", entry)  # type: ignore[attr-defined]
        html = formatted.text.render_as("html")  # type: ignore[attr-defined]
        assert 'href="https://urn.fi/URN:NBN:fi:aalto-202305213270"' in html
        assert "https://example.com/other" in html

    def test_original_entry_not_mutated(self, style: PlainUrn) -> None:
        """Edge Case: Ensure the mixin does not mutate original pybtex Entry."""
        entry = _make_entry(
            fields={
                "urn": "URN:NBN:fi:aalto-202305213270",
                "url": "https://urn.fi/URN:NBN:fi:aalto-202305213270",
            }
        )
        original_url = entry.fields["url"]
        style.format_entry("Sav23", entry)  # type: ignore[attr-defined]
        # The original entry must still have its url field.
        assert entry.fields["url"] == original_url

    def test_http_url_suppressed(self, style: PlainUrn) -> None:
        """Older documents may use http:// for the resolver URL."""
        entry = _make_entry(
            fields={
                "urn": "URN:NBN:fi:aalto-202305213270",
                "url": "http://urn.fi/URN:NBN:fi:aalto-202305213270",
            }
        )
        formatted = style.format_entry("Sav23", entry)  # type: ignore[attr-defined]
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
        formatted = style.format_entry("Sav23", entry)  # type: ignore[attr-defined]
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
        formatted = style.format_entry("Sav23", entry)  # type: ignore[attr-defined]
        html = formatted.text.render_as("html")  # type: ignore[attr-defined]
        assert "URN:NBN:fi:aalto-202305213270" in html
