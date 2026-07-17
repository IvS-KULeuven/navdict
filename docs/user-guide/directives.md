# Directives

Directives are values in the form `<name>//<value>` that navdict resolves when
the value is accessed.

## Common directives

- `yaml//`: load another YAML resource
- `csv//`: load CSV data
- `class//`: import and instantiate a class
- `factory//`: instantiate a factory and call `create()`
- `int-enum//`: create an enum dynamically
- `env//`: read an environment variable

## Basic example

```yaml
setup:
  project_info: yaml//project_info.yaml
```

```python
from navdict import NavDict

setup = NavDict.from_yaml_file("setup.yaml")
print(setup.setup.project_info)
```

The file is loaded when `project_info` is accessed.

## How file paths are resolved

For directives that use file paths:

- Absolute paths are used directly.
- Relative paths are resolved relative to the parent navdict source file, when available.
- If no source file location is available, `NAVDICT_DEFAULT_RESOURCE_LOCATION` is used if set.
- Otherwise, relative paths are resolved from the current working directory.

## Passing directive arguments

Use sibling keys named `<key>_args` and `<key>_kwargs` to pass arguments.

```yaml
setup:
  hk_metrics: csv//data/hk_metrics_daq.csv
  hk_metrics_kwargs:
    header_rows: 2
```

## Environment variables in `csv//`

The `csv//` directive supports `ENV[VARNAME]` in resource paths.

```yaml
setup:
  hk_metrics: csv//ENV[DATA_STORAGE]/hk_metrics_daq.csv
```

If `DATA_STORAGE` is unset, navdict raises a `ValueError`.

Disable environment expansion when needed:

```yaml
setup:
  hk_metrics: csv//ENV[DATA_STORAGE]/hk_metrics_daq.csv
  hk_metrics_kwargs:
    expand_env: false
```

## Next

For directive plugin implementation details, see
[Developer Guide: Directive Plugins](../developer-guide/directive-plugins.md).
