"""Pybtex style mixin and pre-built styles with URN field support."""

from __future__ import annotations

import copy
import logging
from typing import TYPE_CHECKING

from pybtex.richtext import HRef, Text
from pybtex.style.formatting.alpha import Style as AlphaBase
from pybtex.style.formatting.plain import Style as PlainBase
from pybtex.style.formatting.unsrt import Style as UnsrtBase
from pybtex.style.formatting.unsrtalpha import Style as UnsrtAlphaBase

if TYPE_CHECKING:
    from pybtex.database import Entry
    from pybtex.style import FormattedEntry

# General URN resolver (although German & Swiss)
URN_RESOLVER_URL: str = "https://nbn-resolving.org/"

# Specific URN:NBN resolvers by country code.
NBN_RESOLVERS: dict[str, str] = {
    "at": "https://resolver.obvsg.at/",
    "cz": "https://resolver.nkp.cz/web/",
    "fi": "https://urn.fi/",
    "hr": "https://urn.nsk.hr/",
    "hu": "https://nbn.urn.hu/resolver/",
    "it": "https://nbn.depositolegale.it/",
    "nl": "https://www.persistent-identifier.nl/",
    "no": "https://www.nb.no/idtjeneste/search.jsf?urn=",
    "se": "https://urn.kb.se/",
    "si": "https://nbn.si/",
}

#: Known resolver base-URLs for the URN infrastructure.
_RESOLVER_PREFIXES: set[str] = {
    URN_RESOLVER_URL,
    *NBN_RESOLVERS.values(),
    # Include http variants for common resolvers
    "http://urn.fi/",
    "http://nbn-resolving.org/",
}

logger = logging.getLogger(__name__)


def resolve_urn(raw: str) -> tuple[str, str] | None:
    """Return ``(url, display_text)`` for a URN value.

    Handles both bare identifiers (e.g., ``URN:NBN:…``) and full resolver URLs.

    Supports country-specific NBN resolvers for:
    AT, CZ, FI, HR, HU, IT, NL, NO, SE, SI.
    Other NBNs (``URN:NBN:…``) resolve via ``https://nbn-resolving.org/``.

    Args:
        raw: The raw URN value, either as a bare identifier or a full URL.

    Returns:
        A tuple of ``(url, display_text)``, or None if the URN type is not supported.
    """
    stripped = raw.strip()
    stripped_lower = stripped.lower()

    if stripped_lower.startswith(("http://", "https://")):
        # Already a full URL – extract the identifier for display.
        url = stripped
        display = stripped.rsplit("/", 1)[-1] if "/" in stripped else stripped
        return url, display

    if not stripped_lower.startswith("urn:nbn:"):
        logger.warning("only 'URN:NBN' identifiers are supported: %s", stripped)
        return None

    display = stripped
    # URN:NBN:<CC>:... or URN:NBN:<CC>-...
    # We want to extract <CC>
    content = stripped_lower[len("urn:nbn:") :]
    if ":" in content:
        country_code = content.split(":", 1)[0]
    elif "-" in content:
        country_code = content.split("-", 1)[0]
    else:
        country_code = ""

    resolver = NBN_RESOLVERS.get(country_code, URN_RESOLVER_URL)
    url = f"{resolver}{stripped}"
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
    URN identifier to the formatted reference.  Supported URN namespaces
    include:

    * ``URN:NBN:fi:...`` - Finnish NBNs (resolves via ``https://urn.fi/``).
    * ``URN:NBN:<CC>:...`` - Country-specific NBNs (e.g. AT, CZ, HR, HU, IT, NL, NO, SE, SI).
    * ``URN:NBN:...``    - Other NBNs (resolves via ``https://nbn-resolving.org/``).

    Note: only ``URN:NBN`` identifiers are officially supported. Other URN types
    will log a warning.

    The Sphinx extension (``sphinxcontrib_bibtex_urn``) dynamically wraps your
    configured style at build time, so it works with *any* pybtex formatting
    style, including third-party ones.

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
        resolved = resolve_urn(urn_value) if urn_value is not None else None

        if resolved is not None:
            # Work on a shallow copy
            entry = copy.copy(entry)
            entry.fields = dict(entry.fields)

            url, display = resolved

            # Suppress a redundant ``url`` field that merely points at the
            # URN resolver for the same identifier. The comparison is
            # case-insensitive because the URN scheme and NID are
            # case-insensitive per RFC 8141 §2.1.
            existing_url = entry.fields.get("url", "")
            if existing_url and _is_redundant_url(existing_url, urn_value):  # type: ignore[arg-type]
                del entry.fields["url"]

        # Delegate to the real style for the bulk of the formatting.
        formatted = super().format_entry(label, entry)  # type: ignore[misc]

        if resolved is not None:
            url, display = resolved
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
