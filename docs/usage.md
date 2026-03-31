# Usage

## Installation

```bash
uv add sphinxcontrib-bibtex-urn          # or: pip install sphinxcontrib-bibtex-urn
```

## Option A — Sphinx extension (recommended)

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

The extension dynamically wraps your chosen style at build time, so it works with **any** pybtex
formatting style — including third-party ones.

## Option B — Direct pybtex style

If you prefer not to use the Sphinx extension, select one of the pre-built styles directly:

```python
extensions = [
    "sphinxcontrib.bibtex",
]

bibtex_default_style = "urn_alpha"   # or urn_plain, urn_unsrt, urn_unsrtalpha
bibtex_bibfiles = ["refs.bib"]
```

### Available pre-built styles

| Style name       | Base style   |
|------------------|--------------|
| `urn_plain`      | `plain`      |
| `urn_unsrt`      | `unsrt`      |
| `urn_alpha`      | `alpha`      |
| `urn_unsrtalpha` | `unsrtalpha` |

## BibTeX entries

Add a `urn` field to your `.bib` entries. All `URN:NBN` namespaces are supported:

```bibtex
% Finnish National Bibliography Number
@mastersthesis{Sav23,
  author = {Niko Savola},
  title  = {Design and modelling of long-coherence qubits using energy
            participation ratios},
  school = {Aalto University},
  year   = {2023},
  month  = {5},
  urn    = {URN:NBN:fi:aalto-202305213270},
}

% German National Bibliography Number
@book{Example23,
  author    = {Author, Example},
  title     = {An Example German Book},
  publisher = {Springer},
  year      = {2023},
  urn       = {URN:NBN:de:101:1-202301011234},
}
```

The identifier is rendered as a hyperlink pointing to the appropriate national resolver or the general
[nbn-resolving.org](https://nbn-resolving.org/) service.

## Supported resolvers

| Country        | Resolver                                                                               |
|----------------|----------------------------------------------------------------------------------------|
| Austria        | [resolver.obvsg.at](https://resolver.obvsg.at/)                                        |
| Czech Republic | [resolver.nkp.cz](https://resolver.nkp.cz/web/)                                       |
| Finland        | [urn.fi](https://urn.fi/)                                                              |
| Croatia        | [urn.nsk.hr](https://urn.nsk.hr/)                                                      |
| Hungary        | [nbn.urn.hu](https://nbn.urn.hu/resolver/)                                             |
| Italy          | [nbn.depositolegale.it](https://nbn.depositolegale.it/)                                |
| Netherlands    | [persistent-identifier.nl](https://www.persistent-identifier.nl/)                      |
| Norway         | [nb.no](https://www.nb.no/idtjeneste/search.jsf?urn=)                                 |
| Sweden         | [urn.kb.se](https://urn.kb.se/)                                                        |
| Slovenia       | [nbn.si](https://nbn.si/)                                                              |
| Other          | [nbn-resolving.org](https://nbn-resolving.org/) (fallback)                             |

## URNs in the `url` field

If the `urn` field is missing, the plugin also scans the `url` field. If it contains a link to a supported
URN resolver (e.g., `https://urn.fi/…` or `https://nbn-resolving.org/…`), it is automatically
**promoted** and formatted as a hyperlinked URN identifier.

If the entry contains both a `urn` field and a `url` field pointing at the same resolver, the redundant
URL is automatically suppressed to avoid duplication. The comparison is case-insensitive per
[RFC 8141](https://datatracker.ietf.org/doc/html/rfc8141) and handles both `http://` and `https://`
resolver URLs.

## How it works

The plugin provides `UrnStyleMixin`, a pybtex style mixin that overrides `format_entry` to append a
hyperlinked URN when the field is present. The Sphinx extension (`sphinxcontrib_bibtex_urn`) dynamically
wraps your configured style at build time, so it works with *any* pybtex formatting style, including
third-party ones.
