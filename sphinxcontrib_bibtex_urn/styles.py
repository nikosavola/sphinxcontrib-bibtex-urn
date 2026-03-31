"""Pybtex style mixin and pre-built styles with URN field support."""

from __future__ import annotations

import copy
from typing import TYPE_CHECKING

from pybtex.richtext import HRef, Text
from pybtex.style.formatting.alpha import Style as AlphaBase
from pybtex.style.formatting.plain import Style as PlainBase
from pybtex.style.formatting.unsrt import Style as UnsrtBase
from pybtex.style.formatting.unsrtalpha import Style as UnsrtAlphaBase

if TYPE_CHECKING:
    from pybtex.database import Entry
    from pybtex.style import FormattedEntry

URN_RESOLVER_URL: str = "https://urn.fi/"

#: Known resolver base-URLs for the Finnish URN infrastructure.  Both
#: ``http`` and ``https`` variants appear in the wild (older documents
#: used plain HTTP).
_RESOLVER_PREFIXES: set[str] = {
    "https://urn.fi/",
    "http://urn.fi/",
}


def _resolve_urn(raw: str) -> tuple[str, str]:
    """Return ``(url, display_text)`` for a URN value.

    Handles both bare identifiers (e.g., ``URN:NBN:fi:…``, ``URN:ISBN:…``,
    ``URN:ISSN:…``) and full resolver URLs (e.g., ``https://urn.fi/URN:NBN:fi:…``).

    Args:
        raw: The raw URN value, either as a bare identifier or a full URL.

    Returns:
        A tuple of ``(url, display_text)``.
    """
    stripped = raw.strip()
    if stripped.lower().startswith(("http://", "https://")):
        # Already a full URL – extract the identifier for display.
        url = stripped
        display = stripped.rsplit("/", 1)[-1] if "/" in stripped else stripped
    else:
        display = stripped
        url = f"{URN_RESOLVER_URL}{stripped}"
    return url, display


def _is_redundant_url(url: str, urn_value: str) -> bool:
    """Check if a URL is a redundant URN resolver link for a given identifier.

    The check is case-insensitive for the scheme, host, and URN prefix
    (``URN:NID:…``) because the URN scheme and Namespace Identifier are
    case-insensitive per RFC 8141 §2.1.

    Args:
        url: The URL to check.
        urn_value: The URN identifier value to compare against.

    Returns:
        True if the URL is a redundant resolver link, False otherwise.
    """
    url_lower = url.strip().lower()
    urn_lower = urn_value.strip().lower()
    # Direct substring match (case-insensitive).
    if urn_lower in url_lower:
        return True
    # Check if the URL is a known resolver link for this URN.
    for prefix in _RESOLVER_PREFIXES:
        if url_lower.startswith(prefix) or url_lower.startswith(
            prefix.replace("https://", "http://")
        ):
            url_urn_part = url.strip()[len(prefix) :]
            if url_urn_part.lower() == urn_lower:
                return True
    return False


class UrnStyleMixin:
    """Mixin that adds a ``urn`` BibTeX field to any pybtex formatting style.

    When an entry contains a ``urn`` field the mixin appends a hyperlinked
    URN identifier to the formatted reference.  All Finnish URN namespaces
    are supported, including:

    * ``URN:NBN:fi:...`` - National Bibliography Numbers
    * ``URN:ISBN:...``     - ISBN-based URNs
    * ``URN:ISSN:...``     - ISSN-based URNs

    The identifier is rendered as a hyperlink pointing at the National
    Library of Finland's resolver (``https://urn.fi/``).

    If the entry also carries a ``url`` field whose value points at the
    same resolver URL the redundant URL is suppressed automatically.  The
    comparison is case-insensitive per :rfc:`8141`.
    """

    def format_entry(self, label: str, entry: Entry) -> FormattedEntry:
        """Format an entry, appending a URN hyperlink when the field exists.

        Args:
            label: The entry label.
            entry: The BibTeX entry to format.

        Returns:
            The formatted entry with URN support.
        """
        urn_value: str | None = entry.fields.get("urn")

        if urn_value is not None:
            # Work on a shallow copy
            entry = copy.copy(entry)
            entry.fields = dict(entry.fields)

            url, display = _resolve_urn(urn_value)

            # Suppress a redundant ``url`` field that merely points at the
            # URN resolver for the same identifier. The comparison is
            # case-insensitive because the URN scheme and NID are
            # case-insensitive per RFC 8141 §2.1.
            existing_url = entry.fields.get("url", "")
            if existing_url and _is_redundant_url(existing_url, urn_value):
                del entry.fields["url"]

        # Delegate to the real style for the bulk of the formatting.
        formatted = super().format_entry(label, entry)  # type: ignore[misc]

        if urn_value is not None:
            url, display = _resolve_urn(urn_value)
            urn_href = HRef(url, Text(display))
            formatted.text = Text(formatted.text, " ", urn_href, ".")

        return formatted


# Pre-built wrapped styles registered as pybtex entry-points so that
# users can simply set  bibtex_default_style = "urn_alpha"  etc.


class PlainUrn(UrnStyleMixin, PlainBase):  # type: ignore[misc]
    """``plain`` style with URN support."""


class UnsrtUrn(UrnStyleMixin, UnsrtBase):  # type: ignore[misc]
    """``unsrt`` style with URN support."""


class AlphaUrn(UrnStyleMixin, AlphaBase):  # type: ignore[misc]
    """``alpha`` style with URN support."""


class UnsrtAlphaUrn(UrnStyleMixin, UnsrtAlphaBase):  # type: ignore[misc]
    """``unsrtalpha`` style with URN support."""
