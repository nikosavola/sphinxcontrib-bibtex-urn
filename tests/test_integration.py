"""Integration tests for the Sphinx extension."""

from __future__ import annotations

from pathlib import Path

import pytest
from sphinx.application import Sphinx


@pytest.fixture
def sphinx_app(tmp_path: Path) -> Sphinx:
    """Create a minimal Sphinx application for testing."""
    src_dir = tmp_path / "src"
    conf_dir = tmp_path / "src"
    out_dir = tmp_path / "out"
    doctree_dir = tmp_path / "doctrees"

    src_dir.mkdir()
    out_dir.mkdir()
    doctree_dir.mkdir()

    # Create a minimal conf.py
    conf_py = src_dir / "conf.py"
    conf_py.write_text(
        "extensions = ['sphinxcontrib.bibtex', 'sphinxcontrib_bibtex_urn']\n"
        "bibtex_bibfiles = ['refs.bib']\n"
        "bibtex_default_style = 'alpha'\n"
    )

    # Create a minimal refs.bib
    refs_bib = src_dir / "refs.bib"
    refs_bib.write_text(
        "@article{test2024,\n"
        "  author = {Tester, Test},\n"
        "  title = {A Test Article},\n"
        "  journal = {Journal of Testing},\n"
        "  year = {2024},\n"
        "  urn = {URN:NBN:fi:aalto-202305213270}\n"
        "}\n"
    )

    # Create a minimal index.rst
    index_rst = src_dir / "index.rst"
    index_rst.write_text("Test\n====\n\nSee :cite:`test2024`.\n\n.. bibliography::\n")

    return Sphinx(
        srcdir=str(src_dir),
        confdir=str(conf_dir),
        outdir=str(out_dir),
        doctreedir=str(doctree_dir),
        buildername="html",
    )


def test_extension_integration(sphinx_app: Sphinx) -> None:
    """End-to-end test: building with the extension should succeed and apply the style."""
    # Ensure the builder-inited signal was connected and fired
    # (Sphinx constructor already initialized everything)

    # Verify the style was patched
    assert sphinx_app.config.bibtex_default_style == "_urn_wrapped_alpha"

    # Run the build
    sphinx_app.build()

    # Check if the output contains the hyperlinked URN
    output_html = (Path(sphinx_app.outdir) / "index.html").read_text()
    assert "URN:NBN:fi:aalto-202305213270" in output_html
    assert 'href="https://urn.fi/URN:NBN:fi:aalto-202305213270"' in output_html
