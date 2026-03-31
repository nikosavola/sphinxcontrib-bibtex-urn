# AGENTS.md

## Project overview

sphinxcontrib-bibtex-urn is a Sphinx/pybtex extension that adds URN:NBN (National Bibliography Number) support to
bibliographies managed by sphinxcontrib-bibtex. It renders BibTeX `urn` fields as hyperlinked identifiers using
country-specific resolvers.

## Setup

```bash
just install
```

This installs all dependencies (including dev, lint, test, and docs groups) via `uv sync` and sets up pre-commit hooks.

## Required before creating a PR or a new commit

1. Run pre-commit hooks: `just pre-commit`
2. Run tests: `just test`
3. Compile docs: `just docs`

All three must pass before committing or opening a PR.

## Code style

- Python 3.10+ syntax (use modern typing, `|` unions, etc.)
- Formatting and linting enforced by Ruff (config in `pyproject.toml`)
- Google-style docstrings, enforced by `interrogate` at 100% coverage (excluding tests and `__init__.py`)
- Imports sorted by isort (via Ruff) with `combine-as-imports`

## Testing

- Framework: pytest with pytest-xdist for parallel execution
- Run: `just test` (equivalent to `uv run --dev pytest -n auto`)
- Additional test dependencies: hypothesis (for fuzzing), pycountry, pydantic
- Tests live in `tests/` directory (`test_styles.py`, `test_extension.py`, `test_integration.py`)

## Documentation

- Built with Sphinx using MyST (Markdown) parser and the shibuya theme
- Source files in `docs/`
- Build: `just docs` (produces HTML in `docs/_build/html`)
- API docs auto-generated via sphinx-autoapi

## Project structure

- `sphinxcontrib_bibtex_urn/` -- main package source
  - `__init__.py` -- Sphinx extension entry point and dynamic style patching
  - `styles.py` -- URN resolution logic, `UrnStyleMixin`, and pre-built styles
- `tests/` -- test suite
- `docs/` -- Sphinx documentation source
- `justfile` -- development task runner (use `just --list` to see all recipes)
- `pyproject.toml` -- project metadata, dependencies, and tool configuration
