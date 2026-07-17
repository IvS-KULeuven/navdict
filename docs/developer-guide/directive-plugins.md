# Directive Plugins

Directive plugins let you extend navdict with custom `<name>//...` values.

## Function signature

A plugin function should use this interface:

```python
def load_something(value: str, parent_location: Path | None, *args, **kwargs):
    ...
```

- `value`: text after `//`
- `parent_location`: source location of the loaded YAML, when available
- `args` and `kwargs`: values passed from sibling YAML keys

## Registering plugins

Register plugins with Python entry points in `pyproject.toml`:

```toml
[project.entry-points."navdict.directive"]
yaml = 'navdict.directives:load_yaml'
csv = 'navdict.directives:load_csv'
env = 'navdict.directives:env_var'
```

You can also register plugins programmatically at runtime.

## Register plugins at runtime

Use `register_directive` for process-local registration:

```python
from pathlib import Path

from navdict.directive import register_directive


def txt_loader(value: str, parent_location: Path | None, *args, **kwargs):
    base = parent_location or Path(".")
    path = (base / value).expanduser()
    return path.read_text(encoding="utf-8")


register_directive("txt", txt_loader)
```

Then use it like any other directive:

```yaml
notes:
  release: txt//notes/release.txt
```

Runtime registration details:

- Registration applies to the current Python process.
- If you register a name that already exists, the new function replaces the old one.
- This mechanism is useful for app-specific directives and tests.

## Passing plugin arguments from YAML

For a key `hk_metrics`, navdict reads:

- `hk_metrics_args` as positional arguments
- `hk_metrics_kwargs` as keyword arguments

```yaml
setup:
  hk_metrics: csv//data/hk_metrics_daq.csv
  hk_metrics_kwargs:
    header_rows: 2
```

## Matching and parsing

Directive values are matched against:

`r"^([a-zA-Z]\w+)/{2}(.*)$`

Group 1 is the directive key, group 2 is the directive payload.
