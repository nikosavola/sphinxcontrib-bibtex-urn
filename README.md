# sphinxcontrib-bibtex-urn

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Test Status](https://github.com/nikosavola/sphinxcontrib-bibtex-urn/actions/workflows/test.yml/badge.svg)](https://github.com/nikosavola/sphinxcontrib-bibtex-urn/actions/workflows/test.yml)

A [Sphinx](https://www.sphinx-doc.org/) plugin that extends
[sphinxcontrib-bibtex](https://sphinxcontrib-bibtex.readthedocs.io/) with support for **Finnish URN identifiers** (and
URNs in general).

BibTeX entries containing a `urn` field are rendered with a hyperlinked identifier, similar to how `doi` fields work:

```bibtex
[Sav23]  Niko Savola. Design and modelling of long-coherence qubits using energy
         participation ratios. Master's thesis, Aalto University, May 2023.
         URN:NBN:fi:aalto-202305213270.
```

where `URN:NBN:fi:aalto-202305213270` is a clickable link pointing to `https://urn.fi/URN:NBN:fi:aalto-202305213270`.

## Installation

```bash
uv add sphinxcontrib-bibtex-urn          # or: pip install sphinxcontrib-bibtex-urn
```

## Usage

### Option A – Sphinx extension (recommended)

Add the extension to your `conf.py` **after** `sphinxcontrib.bibtex`. It automatically wraps whatever
`bibtex_default_style` you have configured:

```python
extensions = [
    "sphinxcontrib.bibtex",
    "sphinxcontrib_bibtex_urn",
]

bibtex_default_style = "alpha"    # any pybtex style works
bibtex_bibfiles = ["refs.bib"]
```

### Option B – Direct pybtex style

If you prefer not to use the Sphinx extension, select one of the pre-built styles directly:

```python
extensions = [
    "sphinxcontrib.bibtex",
]

bibtex_default_style = "urn_alpha"   # or urn_plain, urn_unsrt, urn_unsrtalpha
bibtex_bibfiles = ["refs.bib"]
```

### BibTeX entries

Add a `urn` field to your `.bib` entries. All URN namespaces resolved by the National Library of Finland are supported:

```bibtex
% URN:NBN – National Bibliography Number (thesis, reports, …)
@mastersthesis{Sav23,
  author = {Niko Savola},
  title  = {Design and modelling of long-coherence qubits using energy
            participation ratios},
  school = {Aalto University},
  year   = {2023},
  month  = {5},
  urn    = {URN:NBN:fi:aalto-202305213270},
}

% URN:ISBN – book identified by ISBN
@book{Example23,
  author    = {Author, Example},
  title     = {An Example Book},
  publisher = {WSOY},
  year      = {2023},
  urn       = {URN:ISBN:978-951-51-7661-5},
}

% URN:ISSN – serial identified by ISSN
@article{Serial22,
  author  = {Writer, Serial},
  title   = {An Example Article},
  journal = {Example Journal},
  year    = {2022},
  urn     = {URN:ISSN:1234-5678},
}
```

The identifier is rendered as a hyperlink pointing to the National Library of Finland's resolver at `https://urn.fi/`.
For instance, `URN:NBN:fi:aalto-202305213270` links to `https://urn.fi/URN:NBN:fi:aalto-202305213270`.

If the entry also contains a `url` field pointing at the same resolver URL, it is automatically suppressed to avoid
duplication. The comparison is case-insensitive (per [RFC 8141](https://datatracker.ietf.org/doc/html/rfc8141)) and
handles both `http://` and `https://` resolver URLs.

## How it works

The plugin provides `UrnStyleMixin`, a pybtex style mixin that overrides `format_entry` to append a hyperlinked URN when
the field is present. The Sphinx extension (`sphinxcontrib_bibtex_urn`) dynamically wraps your configured style at build
time, so it works with *any* pybtex formatting style, including third-party ones.

## Development

For information on how to set up the development environment, run tests, and contribute to the project, please see
[CONTRIBUTING.md](CONTRIBUTING.md).
