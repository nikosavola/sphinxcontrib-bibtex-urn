# sphinxcontrib-bibtex-urn

A [Sphinx](https://www.sphinx-doc.org/) plugin that extends
[sphinxcontrib-bibtex](https://sphinxcontrib-bibtex.readthedocs.io/) with support for **URN identifiers** (specifically
National Bibliography Numbers).

BibTeX entries containing a `urn` field are rendered with a hyperlinked identifier, similar to how `doi` fields work:

> [Sav23] Niko Savola. *Design and modelling of long-coherence qubits using energy participation ratios.* Master's
> thesis, Aalto University, May 2023. [URN:NBN:fi:aalto-202305213270](https://urn.fi/URN:NBN:fi:aalto-202305213270).

## Features

- **Country-specific NBNs** — Resolution for National Bibliography Numbers from Austria, Czech Republic, Finland,
  Croatia, Hungary, Italy, Netherlands, Norway, Sweden, and Slovenia.
- **Global NBNs** — Other `URN:NBN:…` identifiers resolved via [nbn-resolving.org](https://nbn-resolving.org/).
- **Auto-deduplication** — Automatically suppresses redundant `url` fields that point to the same URN resolver.
- **URL promotion** — If an entry has no `urn` field but its `url` points to a known resolver, it is automatically
  promoted and formatted as a URN hyperlink.
- **Any pybtex style** — Works with all built-in and third-party pybtex formatting styles.

## Quick start

Install the package:

```bash
uv add sphinxcontrib-bibtex-urn     # or: pip install sphinxcontrib-bibtex-urn
```

Add the extension to your Sphinx `conf.py`:

```python
extensions = [
    "sphinxcontrib.bibtex",
    "sphinxcontrib_bibtex_urn",
]

bibtex_default_style = "alpha"   # any pybtex style works
bibtex_bibfiles = ["refs.bib"]
```

Then add a `urn` field to your `.bib` entries:

```bibtex
@mastersthesis{Sav23,
  author = {Niko Savola},
  title  = {Design and modelling of long-coherence qubits},
  school = {Aalto University},
  year   = {2023},
  urn    = {URN:NBN:fi:aalto-202305213270},
}
```

See the {doc}`usage` guide for full details and the {doc}`examples` page for rendered citation style demos.

```{toctree}
:maxdepth: 2
:caption: Documentation

usage
examples
api
```

```{toctree}
:maxdepth: 1
:caption: Project

contributing
security
changelog
```
