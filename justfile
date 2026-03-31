# Default to listing available recipes
default:
    @just --list

cpus := num_cpus()

# --- Installation ---

# Install the package and all development dependencies
[group('setup')]
install:
    @uv sync --all-groups
    @uv run prek install

# Clean up all build, test, coverage and Python artifacts
[confirm]
[group('setup')]
clean:
    @rm -rf dist build *.egg-info .ruff_cache .pytest_cache htmlcov coverage.xml docs/_build

# --- Linting & Formatting ---

# Update pre-commit hooks to the latest revisions
[group('lint')]
update-pre:
    @uvx prek autupdate -j $(( {{ cpus }} / 2 + {{ cpus }} % 2 ))

# Run all pre-commit hooks on all files
[group('lint')]
pre-commit:
    @uvx prek run --all-files

# --- Testing ---

# Run tests with pytest
[group('test')]
test *args:
    uv run --dev pytest -n auto {{ args }}

# --- Documentation ---

# Build the documentation as HTML
[group('docs')]
docs: docs-html

# Build the documentation as HTML
[group('docs')]
docs-html:
    @uv run --group docs sphinx-build -b html docs docs/_build/html

# Build the documentation as LaTeX
[group('docs')]
docs-latex:
    @uv run --group docs sphinx-build -b latex docs docs/_build/latex

# Build the documentation as PDF (requires LaTeX)
[env('XINDYOPTS', '-M sphinx.xdy')]
[group('docs')]
[working-directory('docs/_build/latex')]
docs-pdf: docs-latex
    latexmk -pdfxe -interaction=nonstopmode -f -file-line-error

# --- Build ---

# Build the Python package
[group('build')]
build:
    @rm -rf dist
    uv build
