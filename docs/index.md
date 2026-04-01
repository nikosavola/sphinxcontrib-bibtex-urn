# sphinxcontrib-bibtex-urn

```{include} ../README.md
:start-after: "<!-- intro-start -->"
:end-before: "<!-- intro-end -->"
```

## Features

```{include} ../README.md
:start-after: "<!-- features-start -->"
:end-before: "<!-- features-end -->"
```

## Quick start

### Installation

```{include} ../README.md
:start-after: "<!-- installation-start -->"
:end-before: "<!-- installation-end -->"
```

### Usage

Add the extension to your Sphinx `conf.py`:

```python
extensions = [
    "sphinxcontrib.bibtex",
    "sphinxcontrib_bibtex_urn",
]

bibtex_default_style = "alpha"   # any pybtex style works
bibtex_bibfiles = ["refs.bib"]
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
code_of_conduct
security
```
