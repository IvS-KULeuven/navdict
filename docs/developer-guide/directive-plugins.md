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
