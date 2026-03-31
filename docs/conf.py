"""Sphinx configuration for sphinxcontrib-bibtex-urn documentation."""

project = "sphinxcontrib-bibtex-urn"
copyright = "2025, Niko Savola"  # noqa: A001
author = "Niko Savola"
release = "0.1.0"

extensions = [
    "sphinxcontrib.mermaid",
    "myst_parser",
    "sphinx.ext.intersphinx",
    "sphinx_copybutton",
    "sphinxcontrib.bibtex",
    "sphinxcontrib_bibtex_urn",
    "autoapi.extension",
]

# -- MyST settings ----------------------------------------------------------
myst_enable_extensions = [
    "colon_fence",
    "fieldlist",
]
myst_fence_as_directive = ["mermaid"]

# -- Theme -------------------------------------------------------------------
html_theme = "shibuya"
html_theme_options = {
    "github_url": "https://github.com/nikosavola/sphinxcontrib-bibtex-urn",
    "accent_color": "blue",
    "globaltoc_expand_depth": 2,
    "discussion_url": "https://github.com/nikosavola/sphinxcontrib-bibtex-urn/discussions",
    "nav_links": [
        {
            "title": "PDF",
            "url": "https://nikosavola.github.io/sphinxcontrib-bibtex-urn/sphinxcontrib-bibtex-urn.pdf",
        },
        {"title": "PyPI", "url": "https://pypi.org/project/sphinxcontrib-bibtex-urn/"},
    ],
    "pygments_light_style": "tango",
    "pygments_dark_style": "dracula",
}
html_context = {
    "github_user": "nikosavola",
    "github_repo": "sphinxcontrib-bibtex-urn",
    "github_version": "main",
    "doc_path": "docs",
}
html_static_path = ["_static"]
html_title = "sphinxcontrib-bibtex-urn"

# -- Bibliography ------------------------------------------------------------
bibtex_bibfiles = ["bibliography.bib"]
bibtex_default_style = "alpha"

# -- Intersphinx -------------------------------------------------------------
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "sphinx": ("https://www.sphinx-doc.org/en/master", None),
    "pybtex": ("https://docs.pybtex.org/", None),
}
# -- AutoAPI -----------------------------------------------------------------
autoapi_dirs = ["../sphinxcontrib_bibtex_urn"]
autoapi_type = "python"
autoapi_options = [
    "members",
    "undoc-members",
    "show-inheritance",
    "show-module-summary",
]
autoapi_ignore = ["**/test_*"]
autoapi_add_toctree_entry = False

# -- Mermaid -----------------------------------------------------------------
mermaid_output_format = "raw"

# -- LaTeX -------------------------------------------------------------------
latex_engine = "xelatex"
latex_use_xindy = True
latex_show_pagerefs = True
latex_show_urls = "footnote"
latex_documents = [
    (
        "index",
        "sphinxcontrib-bibtex-urn.tex",
        "sphinxcontrib-bibtex-urn",
        "Niko Savola",
        "manual",
    ),
]
latex_elements = {
    "papersize": "a4paper",
    "pointsize": "10pt",
    "fncychap": "\\usepackage[Bjornstrup]{fncychap}",
    "preamble": r"""
\ChNumVar{\fontsize{60}{62}\usefont{OT1}{ptm}{m}{n}\selectfont}
\ChTitleVar{\Huge\bfseries\scshape}
""",
}

# -- Misc --------------------------------------------------------------------

suppress_warnings = ["misc.highlighting_failure"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
