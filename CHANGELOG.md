# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.11.0] - 2026-07-17

- Documentation updated: separate and enhance user and developer docs
- Added navdict logo `[.]`
- Updated README

## [0.10.0] - 2026-07-16

### Fixed

- Fixed alias hook exception handling in NavigableDict. When an alias still returns an unknown attribute, don't log an error message.

## [0.9.0] - 2026-07-14

### Added

- Type-stub support for dynamic attribute access on `NavigableDict` to reduce PyLance attribute-access warnings.
- `NavigableDict.as_typed(schema_type)` helper for schema-based type hints and improved editor auto-completion.

### Changed

- `NavigableDict.__dir__()` now includes identifier-like dictionary keys to improve interactive discoverability.

### Fixed

- Missing `expand_env_vars` declaration in stubs, removing an unknown-import warning in static analysis.
- `is_directive` stub typing now accepts non-string inputs used in tests.

## [0.8.0] - 2026-07-13

### Added

- `expand_env_vars` function is now explicitly exported from the main module (public API)
- `get_resource_location` function is now explicitly exported from the main module (public API)
- `load_yaml` directive now supports `expand_env` kwarg (default `True`) for environment variable expansion in resource paths
- Enhanced logging: debug logs for `load_yaml`, `load_csv`, and `env_var` directive plugins

### Fixed

- `get_resource_location` now correctly handles tilde (`~`) expansion for home directory paths
- `expand_env_vars` responsibility clarified: no longer applies path expansion (handled by `get_resource_location`)
- `load_yaml` now properly forwards `*args` and `**kwargs` to the underlying loader
- `load_yaml` function signature corrected (`parent_location` parameter is now required, not optional)
- Added validation for empty resource names in `load_yaml` and `load_csv`

### Changed

- `expand_env_vars` behavior changed: no longer applies `~` expansion (that's now `get_resource_location`'s responsibility)
- Logging levels adjusted: `load_csv` uses `logger.info` instead of commented-out debug log

## [0.7.0] - 2026-07-10

### Added

- `csv//` directive: `ENV[VARNAME]` (also `ENV['VARNAME']` / `ENV["VARNAME"]`) expansion of
  environment variables in the resource path, with `~` expansion applied to the result. Controlled
  by a new `expand_env` kwarg (default `True`).
- A test demonstrating a user-defined directive plugin (`pandas//`) registered via
  `register_directive()`.
- A marimo-based tutorial notebook (`demo/tutorial.py`) covering creation, dot navigation,
  directives, and aliases.
- `python -m navdict` entry point (`src/navdict/__main__.py`) printing a link to the docs.
- `RELEASE.md` release checklist.
- `CLAUDE.md` guidance for Claude Code when working in this repository.

### Fixed

- Nested `NavigableDict` values created via `add()`, `__setattr__()`, and `__setitem__()` now
  correctly receive their `label` (previously only `__init__()` did this).

### Changed

- `.gitignore` now ignores `.DS_Store`.
- Added a `demo` dependency group (`marimo`) to `pyproject.toml` for the tutorial notebook.

## [0.6.3] - 2025-10-17

### Fixed

- Alias hook function raising an exception is now handled gracefully instead of propagating.

## [0.6.2] - 2025-10-17

### Fixed

- `_alias_hook` lookup in `NavigableDict.__getitem__()`.

## [0.6.1] - 2025-10-17

### Fixed

- Directive loading when resolving an alias via the alias hook.

## [0.6.0] - 2025-10-16

### Added

- Alias hooks: `set_alias_hook()` lets a `NavigableDict` map alternate names to a valid
  attribute/key via a user-supplied function.

## [0.5.9] - 2025-08-12

### Fixed

- Removed a leftover debug print statement.

## [0.5.8] - 2025-08-11

### Fixed

- Directive loading when initializing a `NavigableDict`.

## [0.5.7] - 2025-08-11

### Added

- `NAVDICT_DEFAULT_RESOURCE_LOCATION` environment variable as a fallback resource location for
  directives when no parent location is known.

## [0.5.6] - 2025-08-11

### Added

- `register_directive()` for registering custom directive plugins at runtime.

## [0.5.5] - 2025-08-11

### Fixed

- `csv//` directive loading and proper access to a `NavigableDict`'s label.

## [0.5.4] - 2025-08-11

### Fixed

- `to_yaml_file()` when `_filename` is `None`.

## [0.5.3] - 2025-08-11

### Added

- Optional `header` and `top_level_group` arguments to `to_yaml_file()`.

## [0.5.2] - 2025-08-08

### Fixed

- `ScannerError` raised while reading an invalid YAML file is now handled and re-raised as a
  clearer `IOError`.

## [0.5.1] - 2025-08-08

### Fixed

- Access to non-string keys.

## [0.5.0] - 2025-08-08

### Added

- `env//` directive for reading environment variables.
- Documentation for the directive plugin system.

## [0.4.0] - 2025-07-04

### Changed

- Refactored to a pluggable directive architecture (directive plugins registered via entry points
  or `register_directive()`).
- Cleaned up log messages; made the codebase mypy-clean; applied `ruff format`.

### Added

- Initial project documentation.

## [0.3.2] - 2025-07-03

### Changed

- Made the codebase mypy-compliant.

## [0.3.1] - 2025-07-02

### Fixed

- `~` (user home directory) expansion in directive resource paths.

## [0.3.0] - 2025-07-01

### Added

- Support for relative paths in directives.
- Initial documentation.

### Changed

- Dropped Python 3.9 support; Python 3.10+ is now required.

## [0.2.5] - 2025-06-06

### Changed

- Cleaned up `__getattribute__()`/`__getitem__()` and fixed handling of directive `args`/`kwargs`.

## [0.2.4] - 2025-06-06

### Added

- `csv//` directive for loading CSV files.

## [0.2.3] - 2025-06-05

### Fixed

- `__repr__()` and `from_yaml_file()`.

### Added

- Unit test for the `int_enum//` directive.

## [0.2.2] - 2025-06-05

### Fixed

- `__repr__()`; `from_yaml_file()` now returns a `navdict` instance.

## [0.2.1] - 2025-06-05

### Changed

- Updated the README.

## [0.2.0] - 2025-06-04

### Added

- Initial fully working `navdict` (project renamed from its original name).

## [0.1.0] - 2025-06-04

### Added

- Initial commit.

---

[Unreleased]: https://github.com/IvS-KULeuven/navdict/compare/0.11.0...HEAD
[0.11.0]: https://github.com/IvS-KULeuven/navdict/releases/tag/0.11.0
[0.10.0]: https://github.com/IvS-KULeuven/navdict/releases/tag/0.10.0
[0.9.0]: https://github.com/IvS-KULeuven/navdict/releases/tag/0.9.0
[0.8.0]: https://github.com/IvS-KULeuven/navdict/releases/tag/0.8.0
[0.7.0]: https://github.com/IvS-KULeuven/navdict/releases/tag/0.7.0
[0.6.3]: https://github.com/IvS-KULeuven/navdict/releases/tag/0.6.3
[0.6.2]: https://github.com/IvS-KULeuven/navdict/releases/tag/0.6.2
[0.6.1]: https://github.com/IvS-KULeuven/navdict/releases/tag/0.6.1
[0.6.0]: https://github.com/IvS-KULeuven/navdict/compare/0.5.9...9702178
[0.5.9]: https://github.com/IvS-KULeuven/navdict/releases/tag/0.5.9
[0.5.8]: https://github.com/IvS-KULeuven/navdict/compare/515b30a...6b8e41d
[0.5.7]: https://github.com/IvS-KULeuven/navdict/compare/fb86d26...515b30a
[0.5.6]: https://github.com/IvS-KULeuven/navdict/compare/905c83a...fb86d26
[0.5.5]: https://github.com/IvS-KULeuven/navdict/compare/2a37491...905c83a
[0.5.4]: https://github.com/IvS-KULeuven/navdict/compare/5508e0f...2a37491
[0.5.3]: https://github.com/IvS-KULeuven/navdict/compare/47b2122...5508e0f
[0.5.2]: https://github.com/IvS-KULeuven/navdict/compare/0.5.1...47b2122
[0.5.1]: https://github.com/IvS-KULeuven/navdict/releases/tag/0.5.1
[0.5.0]: https://github.com/IvS-KULeuven/navdict/releases/tag/0.5.0
[0.4.0]: https://github.com/IvS-KULeuven/navdict/releases/tag/0.4.0
[0.3.2]: https://github.com/IvS-KULeuven/navdict/compare/0.3.1...2394792
[0.3.1]: https://github.com/IvS-KULeuven/navdict/releases/tag/0.3.1
[0.3.0]: https://github.com/IvS-KULeuven/navdict/compare/0.2.5...fa0cd99
[0.2.5]: https://github.com/IvS-KULeuven/navdict/releases/tag/0.2.5
[0.2.4]: https://github.com/IvS-KULeuven/navdict/releases/tag/0.2.4
[0.2.3]: https://github.com/IvS-KULeuven/navdict/releases/tag/0.2.3
[0.2.2]: https://github.com/IvS-KULeuven/navdict/releases/tag/0.2.2
[0.2.1]: https://github.com/IvS-KULeuven/navdict/releases/tag/0.2.1
[0.2.0]: https://github.com/IvS-KULeuven/navdict/releases/tag/0.2.0
[0.1.0]: https://github.com/IvS-KULeuven/navdict/commit/9bb4235
