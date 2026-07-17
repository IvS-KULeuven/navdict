# Contributing

## Environment setup

Use uv for dependency and environment management.

```shell
uv sync
```

## Test and quality commands

```shell
uv run pytest tests
uv run ruff check .
uv run ruff format
uv run mypy
```

## Docs

```shell
uv run mkdocs serve
```

## Release notes

For release steps, see `RELEASE.md` in the repository root.
