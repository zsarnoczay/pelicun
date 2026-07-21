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

**Model Library Distributed as a Python Package**: The default damage
and loss model data is now resolved from the
`simcenter-dlml <https://pypi.org/project/simcenter-dlml/>`_ package,
a regular pip-installed dependency of pelicun.

- The model data ships inside the installed package, so
  ``import pelicun`` no longer downloads anything: imports work
  offline (e.g., on HPC compute nodes without internet access) and
  nothing is written into the installation directory at runtime.
- The model library is updated by upgrading the package
  (``pip install --upgrade simcenter-dlml``) instead of running a
  download command. A custom DLML checkout can be used by installing
  it in place of the released package
  (``pip install -e <path-to-checkout>``), replacing the former
  ``DLML_DATA_DIR`` environment variable.
- ``PelicunDefault/`` paths now also accept DLML dataset IDs directly
  (e.g., ``PelicunDefault/seismic/building/component/FEMA P-58 2nd
  Edition/fragility.csv``), in addition to the established method
  aliases (e.g., ``PelicunDefault/FEMA P-58/fragility.csv``).
- Path resolution is now strict: every resolved path points to an
  existing file, and unknown method names or files raise clear errors
  instead of returning paths that fail later.
- ``PelicunDefault/`` paths are separator-tolerant: backslashes and
  mixed separators (e.g., ``PelicunDefault/FEMA P-58\fragility.csv``,
  common in configs written on Windows) are accepted on all
  platforms.

**Network Access Blocked in Tests**: The test suite now blocks
network access by default through pytest-socket
(``--disable-socket --allow-unix-socket``), guaranteeing that no test
silently depends on an internet connection.

**uv-Based Development Environment**: The development environment and
CI are now managed with `uv <https://docs.astral.sh/uv/>`_.

- A committed ``uv.lock`` file pins the full development stack, so
  every contributor and every CI job resolves the exact same
  versions. Runtime dependency ranges for end users are unchanged.
- All CI jobs install their environments with ``uv sync --locked``,
  and the uv version itself is pinned in the workflows. This also
  replaces the archived ``chartboost/ruff-action``; the ruff version
  now comes from the lock file.

**Split Development Extras**: The single ``development`` extra was
reorganized into focused ``test``, ``lint``, and ``doc`` extras that
match how the tools are actually used; ``development`` remains
available as the union of the three.

**Non-Mutating Check Script**: ``run_checks.sh`` was replaced by
``scripts/check.sh``, which only reports problems. CI's static-check
job runs the same tools on the same environment.

Removed
-------

**Runtime Model-Data Download Machinery**: With the model library
installed as a package, the download machinery became dead code and
was removed. This includes the ``pelicun.tools.dlml`` module and the
first-import download hook in ``pelicun/__init__.py``.
``pelicun dlml update`` no longer performs downloads: the subcommand
is now an informational stub that explains the new distribution model
and exits with code 0, so existing automation keeps working. The stub
is planned for removal in pelicun 3.12.

**Legacy Linter Dependencies**: flake8 (and its plugins), pylint (and
its plugin), and pydocstyle were removed from the development
dependencies; their roles have long been covered by ruff. The unused
jsonpath2, sphinx-autoapi, and rendre packages were removed as well.

Fixed
-----
