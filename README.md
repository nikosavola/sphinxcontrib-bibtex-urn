# sphinxcontrib-bibtex-urn

[![Test Status](https://github.com/nikosavola/sphinxcontrib-bibtex-urn/actions/workflows/test.yml/badge.svg)](https://github.com/nikosavola/sphinxcontrib-bibtex-urn/actions/workflows/test.yml)
[![Build Status](https://github.com/nikosavola/sphinxcontrib-bibtex-urn/actions/workflows/build.yml/badge.svg)](https://github.com/nikosavola/sphinxcontrib-bibtex-urn/actions/workflows/build.yml)
[![HTML Docs](https://img.shields.io/badge/%F0%9F%93%84_HTML-Docs-blue?style=flat)](https://nikosavola.github.io/sphinxcontrib-bibtex-urn/)
[![PDF Docs](https://img.shields.io/badge/%F0%9F%93%84_PDF-Docs-blue?style=flat&logo=adobeacrobatreader)](https://nikosavola.github.io/sphinxcontrib-bibtex-urn/sphinxcontrib-bibtex-urn.pdf)
[![PyPI version](https://img.shields.io/pypi/v/sphinxcontrib-bibtex-urn.svg)](https://pypi.org/project/sphinxcontrib-bibtex-urn/)
[![Python version](https://img.shields.io/pypi/pyversions/sphinxcontrib-bibtex-urn.svg)](https://pypi.org/project/sphinxcontrib-bibtex-urn/)
[![PyPI downloads](https://img.shields.io/pypi/dm/sphinxcontrib-bibtex-urn.svg)](https://pypistats.org/packages/sphinxcontrib-bibtex-urn)
[![ZeroVer](https://img.shields.io/badge/versioning-0ver-orange.svg)](https://0ver.org/)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

______________________________________________________________________

<!-- intro-start -->

A [Sphinx](https://www.sphinx-doc.org/) plugin that extends
[sphinxcontrib-bibtex](https://sphinxcontrib-bibtex.readthedocs.io/) with support for **URN identifiers** (specifically
National Bibliography Numbers).

BibTeX entries containing a `urn` field are rendered with a hyperlinked identifier, similar to how `doi` fields work:

> [Sav23] Niko Savola. Design and modelling of long-coherence qubits using energy participation ratios. Master's thesis,
> Aalto University, May 2023. [URN:NBN:fi:aalto-202305213270](https://urn.fi/URN:NBN:fi:aalto-202305213270).

where `URN:NBN:fi:aalto-202305213270` is a clickable link pointing to `https://urn.fi/URN:NBN:fi:aalto-202305213270`.

<!-- intro-end -->

## Features

<!-- features-start -->

- **Country-specific NBNs**: Resolution for National Bibliography Numbers for:
  - 🇦🇹 Austria ([resolver.obvsg.at](https://resolver.obvsg.at/))
  - 🇭🇷 Croatia ([urn.nsk.hr](https://urn.nsk.hr/))
  - 🇨🇿 Czech Republic ([resolver.nkp.cz](https://resolver.nkp.cz/web/))
  - 🇫🇮 Finland ([urn.fi](https://urn.fi/))
  - 🇭🇺 Hungary ([nbn.urn.hu](https://nbn.urn.hu/resolver/))
  - 🇮🇹 Italy ([nbn.depositolegale.it](https://nbn.depositolegale.it/))
  - 🇳🇱 Netherlands ([persistent-identifier.nl](https://www.persistent-identifier.nl/))
  - 🇳🇴 Norway ([nb.no](https://www.nb.no/))
  - 🇸🇮 Slovenia ([nbn.si](https://nbn.si/))
  - 🇸🇪 Sweden ([urn.kb.se](https://urn.kb.se/))
- **Global NBNs**: Other `URN:NBN:...` identifiers resolved via [nbn-resolving.org](https://nbn-resolving.org/).
- **Auto-deduplication**: Automatically suppresses redundant `url` fields that point to the same URN resolver.
- **Any pybtex style**: Works with all built-in and third-party pybtex formatting styles.

<!-- features-end -->

## Installation

<!-- installation-start -->

```bash
uv add sphinxcontrib-bibtex-urn          # or: pip install sphinxcontrib-bibtex-urn
```

<!-- installation-end -->

## Usage

<!-- usage-start -->

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

<!-- usage-end -->

### BibTeX entries

<!-- entries-start -->

Add a `urn` field to your `.bib` entries. All `URN:NBN` namespaces are supported:

```bibtex
% URN:NBN:fi – Finnish National Bibliography Number
@mastersthesis{Sav23,
  author = {Niko Savola},
  title  = {Design and modelling of long-coherence qubits using energy
            participation ratios},
  school = {Aalto University},
  year   = {2023},
  month  = {5},
  urn    = {URN:NBN:fi:aalto-202305213270},
}

% URN:NBN:de – German National Bibliography Number
@book{Example23,
  author    = {Author, Example},
  title     = {An Example German Book},
  publisher = {Springer},
  year      = {2023},
  urn       = {URN:NBN:de:101:1-202301011234},
}
```

The identifier is rendered as a hyperlink pointing to the appropriate national resolver or the general
`nbn-resolving.org` service. For instance, `URN:NBN:fi:aalto-202305213270` links to
`https://urn.fi/URN:NBN:fi:aalto-202305213270`.

<!-- entries-end -->

#### URNs in the `url` field

<!-- url-field-start -->

If the `urn` field is missing, the plugin also scans the `url` field. If it contains a link to a supported URN resolver
(e.g., `https://urn.fi/...` or `https://nbn-resolving.org/...`), it is automatically "promoted" and formatted as a
hyperlinked URN identifier.

If the entry contains both a `urn` field and a `url` field pointing at the same resolver, the redundant URL is
automatically suppressed to avoid duplication. The comparison is case-insensitive (per
[RFC 8141](https://datatracker.ietf.org/doc/html/rfc8141)) and handles both `http://` and `https://` resolver URLs.

<!-- url-field-end -->

## How it works

<!-- how-it-works-start -->

The plugin provides `UrnStyleMixin`, a pybtex style mixin that overrides `format_entry` to append a hyperlinked URN when
the field is present. The Sphinx extension (`sphinxcontrib_bibtex_urn`) dynamically wraps your configured style at build
time, so it works with *any* pybtex formatting style, including third-party ones.

<!-- how-it-works-end -->

## Development

For information on how to set up the development environment, run tests, and contribute to the project, please see
[CONTRIBUTING.md](docs/contributing.md).

All participants are expected to follow the [Code of Conduct](docs/code_of_conduct.md).

See the [Security Policy](docs/security.md) for information on how to report vulnerabilities.
