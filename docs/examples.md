# Citation style examples

This page demonstrates how URN identifiers render with different pybtex citation styles. All examples use the same set
of BibTeX entries with `urn` fields.

## Alpha style

The `alpha` style generates labels from the author name and year (e.g., `[Sav23]`).

This is the style used throughout this documentation (`bibtex_default_style = "alpha"`).

```{bibliography}
:style: urn_alpha
:all:
```

## Plain style

The `plain` style uses numbered labels in order of appearance (e.g., `[1]`, `[2]`).

```{bibliography}
:style: urn_plain
:all:
:keyprefix: plain-
```

## Comparison: with and without URN

Entries **with** a `urn` field get a hyperlinked identifier appended. Entries **without** one render as standard
references. Compare the entries above — for instance, `Knuth86` has no URN and appears as a plain reference, while all
other entries show a clickable URN link.

### Available styles

In addition to the two styles shown above, the following pre-built styles are available:

| Style name       | Base style   | Description                               |
| ---------------- | ------------ | ----------------------------------------- |
| `urn_alpha`      | `alpha`      | Author-year labels, sorted alphabetically |
| `urn_plain`      | `plain`      | Numbered labels, sorted alphabetically    |
| `urn_unsrt`      | `unsrt`      | Numbered labels, in citation order        |
| `urn_unsrtalpha` | `unsrtalpha` | Author-year labels, in citation order     |

All styles append a hyperlinked URN identifier to entries that have a `urn` field. When using the Sphinx extension,
*any* pybtex style (including third-party ones) is automatically wrapped with URN support.

## Special behaviors

### Auto-deduplication

The entry `Korhonen19` has both a `urn` field and a `url` field pointing at the same Finnish URN resolver. The plugin
automatically suppresses the redundant URL, so only the URN hyperlink appears.

### URL promotion

The entry `UrlPromotion23` has no `urn` field, but its `url` points to `https://urn.fi/…`. The plugin automatically
promotes this URL and formats it as a URN hyperlink.
