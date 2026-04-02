"""Sphinx extension that adds Finnish URN identifier support to sphinxcontrib-bibtex.

Usage
-----
Add ``"sphinxcontrib_bibtex_urn"`` to the ``extensions`` list in your Sphinx
``conf.py`` **after** ``"sphinxcontrib.bibtex"``::

    extensions = [
        "sphinxcontrib.bibtex",
        "sphinxcontrib_bibtex_urn",
    ]

The extension automatically wraps whatever ``bibtex_default_style`` you
have configured so that any BibTeX entry containing a ``urn`` field will
render the identifier as a hyperlink to ``https://urn.fi/<URN>``.

Alternatively, you can skip the Sphinx extension and use one of the
pre-registered pybtex styles directly::

    bibtex_default_style = "urn_alpha"  # or urn_plain, urn_unsrt, urn_unsrtalpha
"""

from __future__ import annotations

import logging

from pybtex.plugin import find_plugin, register_plugin
from sphinx.application import Sphinx

from .styles import UrnStyleMixin, resolve_urn

__version__ = "0.1.1"
__all__ = ["UrnStyleMixin", "resolve_urn", "setup"]

logger = logging.getLogger(__name__)


def _patch_style(app: Sphinx) -> None:
    """Wrap the active pybtex style with :class:`UrnStyleMixin` at build time.

    Args:
        app: The Sphinx application object.
    """
    style_name: str = getattr(app.config, "bibtex_default_style", "unsrt")

    try:
        base_style = find_plugin("pybtex.style.formatting", style_name)
    except Exception:
        logger.warning(
            "sphinxcontrib_bibtex_urn: could not find pybtex style %r - "
            "URN field support will not be available.",
            style_name,
        )
        return

    # Nothing to do if the style is already URN-aware.
    if issubclass(base_style, UrnStyleMixin):
        return

    wrapped_name = f"_urn_wrapped_{style_name}"
    wrapped_style = type(
        f"Urn{base_style.__name__}",
        (UrnStyleMixin, base_style),
        {"__module__": __name__},
    )

    register_plugin("pybtex.style.formatting", wrapped_name, wrapped_style)
    app.config.bibtex_default_style = wrapped_name
    logger.debug(
        "sphinxcontrib_bibtex_urn: wrapped style %r -> %r", style_name, wrapped_name
    )


def setup(app: Sphinx) -> dict[str, str | bool]:
    """Register the Sphinx extension.

    Args:
        app: The Sphinx application object.

    Returns:
        A metadata dictionary with extension information.
    """
    app.connect("builder-inited", _patch_style)
    return {
        "version": __version__,
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
