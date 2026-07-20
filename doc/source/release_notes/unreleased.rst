.. _changes_unreleased:

==========
Unreleased
==========

Added
-----

**Python 3.13 Support**: Python 3.13 was added to the CI test matrix
and to the package classifiers, and the package now declares
``requires-python >= 3.9`` explicitly.

Changed
-------

**uv-Based Development Environment**: The development environment and
CI are now managed with `uv <https://docs.astral.sh/uv/>`_.

- A committed ``uv.lock`` file pins the full development stack, so
  every contributor and every CI job resolves the exact same
  versions. Runtime dependency ranges for end users are unchanged.
- All CI jobs install their environments with ``uv sync --locked``,
  and the uv version itself is pinned in the workflows.

**Split Development Extras**: The single ``development`` extra was
reorganized into focused ``test``, ``lint``, and ``doc`` extras that
match how the tools are actually used; ``development`` remains
available as the union of the three.

**Non-Mutating Check Script**: ``run_checks.sh`` was replaced by
``scripts/check.sh``, which only reports problems (the old script ran
``ruff check --fix``, rewriting files as a side effect). CI's
static-check job runs the same tools on the same environment.

Removed
-------

**Legacy Linter Dependencies**: flake8 (and its plugins), pylint (and
its plugin), and pydocstyle were removed from the development
dependencies; their roles have been covered by ruff. The unused
jsonpath2, sphinx-autoapi, and rendre packages were removed as well.

Fixed
-----
