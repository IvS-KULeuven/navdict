# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Working mode: plan mode only

Always work in plan mode in this repository. Before making any code change, present a plan — what
will change and why — and wait for explicit confirmation before editing files or running commands
that change state. The goal is for the user to fully understand what code is being added and how it
works, not just to get the change made. Do not skip straight to implementation, even for changes
that look small or obvious.

## Project overview

`navdict` (aka `NavDict` / `NavigableDict`) is a Python dictionary subclass supporting dot-notation
access (`data.user.name`) in addition to normal `dict` access (`data["user"]["name"]`), plus two
extra features: automatic loading of external resource files (YAML, CSV, env vars, ...) and dynamic
class/factory instantiation, both driven by "directive" strings embedded as dict values (e.g.
`yaml//settings.yaml`, `class//package.module.ClassName`). Published to PyPI, docs built with
MkDocs and hosted via `gh-pages`.

## Commands

This project uses `uv` for environment/dependency management.

```bash
# install/sync all dependency groups (dev, docs are default groups; lint/demo are optional)
uv sync

# run the full test suite (also generates an HTML coverage report via addopts in pyproject.toml)
uv run pytest tests

# run a single test file / test
uv run pytest tests/test_navdict.py
uv run pytest tests/test_navdict.py::test_alias_hook

# lint / format (ruff, line-length = 120)
uv run ruff check .
uv run ruff format

# type checking (mypy config in mypy.ini)
uv run mypy

# docs (mkdocs-material)
uv run mkdocs serve
```

Note: `pytest.ini_options` in `pyproject.toml` sets `addopts = "-ra --cov --cov-branch --cov-report html"`
and `log_cli = true` at DEBUG level, so `pytest` output includes coverage and verbose logs by default.

See `RELEASE.md` for the full release checklist (version bump, build, `uv publish`, `mkdocs gh-deploy`).

## Architecture

Everything lives in `src/navdict/`:

- **`navdict.py`** — the core module. Defines `NavigableDict` (aliased as `navdict` and `NavDict` —
  all three names are equivalent and exported from `__init__.py`). Also contains the builtin
  resource-loading functions (`load_yaml`, `load_csv`, `load_class`, `load_int_enum`,
  `get_resource_location`).
- **`directive.py`** — the directive plugin system: regex-based detection/parsing of directive
  strings (`DIRECTIVE_PATTERN = r"^([a-zA-Z]\w+)/{2}(.*)$"`), the `Directive` wrapper class, and a
  registry (`register_directive`, `get_directive_plugin`) populated both from Python entry points
  (group `navdict.directive`, see `pyproject.toml`) and programmatically.
- **`directives.py`** — the actual builtin directive plugin implementations (`load_yaml`, `load_csv`,
  `env_var`) registered via the `navdict.directive` entry point group in `pyproject.toml`. This
  module doubles as the reference example for anyone implementing a custom directive plugin.
- **`changed.py`** — `ChangeTrackingDict`, a `NavDict` subclass that wraps mutable values
  (list/dict/set) in a `MutableProxy` to detect in-place mutations. Independent/experimental
  feature, not wired into the core `NavigableDict`.
- **`__main__.py`** — trivial, just prints a link to the docs site.
- **`navdict.pyi` / `directive.pyi`** — type stubs shipped alongside the implementation.

### How dot-notation and directives interact

`NavigableDict.__init__` recursively wraps every nested `dict` value into a `NavigableDict` and
mirrors every key onto `self.__dict__` via `setattr`, so keys are simultaneously dict items and
instance attributes. `__setattr__`/`__setitem__` are kept in sync so both access paths always agree.

Directive resolution is lazy and happens on *read*, not on load: `__getattribute__` and `__getitem__`
both check `is_directive(value)` on the stored (raw) string and, if it matches, dispatch through
`_handle_directive`, which:
1. looks up a registered plugin by directive key (`get_directive_plugin`), falling back to builtin
   `class//` / `factory//` / `int_enum//` handling if no plugin is registered for that key;
2. gathers `<key>_args` / `<key>_kwargs` sibling entries as positional/keyword arguments for the
   directive function;
3. resolves relative file paths via `get_resource_location`, relative to the NavDict's own
   `_filename` (tracked as a private attribute, not a dict key) or `NAVDICT_DEFAULT_RESOURCE_LOCATION`;
4. memoizes the resolved result per key (`self.__dict__["_memoized"]`) so a directive is only
   evaluated once — `get_raw_value(key)` bypasses resolution to get the original directive string,
   and `del_memoized_key`/`get_memoized_keys` manage the cache directly.

`__getattribute__` also supports a per-instance **alias hook** (`set_alias_hook`): when a plain
attribute/key lookup fails, it falls back to calling the hook with the missing name and retries with
the returned name, letting a NavDict expose alternate names for the same entry (see `docs/aliases.md`).

Private/internal state (`_label`, `_filename`, `_memoized`, and anything set via
`set_private_attribute`) lives only in `self.__dict__`, never in the underlying `dict` — so it's
excluded from `keys()`, iteration, and YAML serialization (`_save`/`to_yaml_file`).

### Adding a new directive plugin

Directive functions have the signature `func(value: str, parent_location: Path | None, *args, **kwargs)`
and are registered either via the `navdict.directive` entry-point group in `pyproject.toml` or at
runtime via `register_directive(name, func)`. See `docs/directives.md` for the full contract and
`directives.py` for reference implementations.
