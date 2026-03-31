# Usage

## Installation

```{include} ../README.md
:start-after: "<!-- installation-start -->"
:end-before: "<!-- installation-end -->"
```

## Option A — Sphinx extension (recommended)

```{include} ../README.md
:start-after: "### Option A – Sphinx extension (recommended)"
:end-before: "### Option B – Direct pybtex style"
```

The extension dynamically wraps your chosen style at build time, so it works with **any** pybtex formatting style —
including third-party ones.

## Option B — Direct pybtex style

```{include} ../README.md
:start-after: "### Option B – Direct pybtex style"
:end-before: "<!-- usage-end -->"
```

### Available pre-built styles

| Style name       | Base style   |
| ---------------- | ------------ |
| `urn_plain`      | `plain`      |
| `urn_unsrt`      | `unsrt`      |
| `urn_alpha`      | `alpha`      |
| `urn_unsrtalpha` | `unsrtalpha` |

## BibTeX entries

```{include} ../README.md
:start-after: "<!-- entries-start -->"
:end-before: "<!-- entries-end -->"
```

The identifier is rendered as a hyperlink pointing to the appropriate national resolver or the general
[nbn-resolving.org](https://nbn-resolving.org/) service.

## Supported resolvers

| Country        | Resolver                                                          |
| -------------- | ----------------------------------------------------------------- |
| Austria        | [resolver.obvsg.at](https://resolver.obvsg.at/)                   |
| Czech Republic | [resolver.nkp.cz](https://resolver.nkp.cz/web/)                   |
| Finland        | [urn.fi](https://urn.fi/)                                         |
| Croatia        | [urn.nsk.hr](https://urn.nsk.hr/)                                 |
| Hungary        | [nbn.urn.hu](https://nbn.urn.hu/resolver/)                        |
| Italy          | [nbn.depositolegale.it](https://nbn.depositolegale.it/)           |
| Netherlands    | [persistent-identifier.nl](https://www.persistent-identifier.nl/) |
| Norway         | [nb.no](https://www.nb.no/idtjeneste/search.jsf?urn=)             |
| Sweden         | [urn.kb.se](https://urn.kb.se/)                                   |
| Slovenia       | [nbn.si](https://nbn.si/)                                         |
| Other          | [nbn-resolving.org](https://nbn-resolving.org/) (fallback)        |

## URNs in the `url` field

```{include} ../README.md
:start-after: "<!-- url-field-start -->"
:end-before: "<!-- url-field-end -->"
```

## How it works

```{include} ../README.md
:start-after: "<!-- how-it-works-start -->"
:end-before: "<!-- how-it-works-end -->"
```
