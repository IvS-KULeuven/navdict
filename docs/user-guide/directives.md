# Directives

Directives are values in the form `<name>//<value>` that navdict resolves when
the value is accessed.

## Common directives

- `yaml//`: load another YAML resource
- `csv//`: load CSV data
- `class//`: import and instantiate a class
- `factory//`: instantiate a factory and call `create()`
- `int_enum//`: create an enum dynamically
- `env//`: read an environment variable

## Directive behavior at a glance

- Directive values are resolved lazily: on access, not on load.
- For plugin-backed directives, resolved values are memoized per key.
- Use `get_raw_value(key)` if you need the original directive string.

## `yaml//`: load nested YAML

```yaml
setup:
  project_info: yaml//project_info.yaml
```

```python
from navdict import NavDict

setup = NavDict.from_yaml_file("setup.yaml")
print(setup.setup.project_info)
```

The referenced YAML is loaded when `project_info` is accessed.

You can pass options via sibling kwargs:

```yaml
setup:
  project_info: yaml//project_info.yaml
  project_info_kwargs:
    expand_env: false
```

## `csv//`: load CSV data

```yaml
telemetry:
  hk_metrics: csv//data/hk_metrics_daq.csv
  hk_metrics_kwargs:
    header_rows: 2
    delimiter: ';'
```

```python
from navdict import NavDict

cfg = NavDict.from_yaml_file("setup.yaml")
rows = cfg.telemetry.hk_metrics
print(rows[0])
```

Supported CSV kwargs include:

- `header_rows`: number of lines skipped before parsing.
- `delimiter`: CSV delimiter character.
- `expand_env`: enable or disable `ENV[...]` expansion.

## `class//`: import and instantiate a class

```yaml
devices:
  controller: class//mypkg.control.Controller
  controller_args: ["CTRL-01"]
  controller_kwargs:
    simulate: true
```

```python
cfg = NavDict.from_yaml_file("setup.yaml")
controller = cfg.devices.controller
```

The class is imported dynamically and called as:

`Controller(*controller_args, **controller_kwargs)`

## `factory//`: instantiate factory and call `create()`

```yaml
devices:
  detector: factory//mypkg.factories.DetectorFactory
  detector_args:
    model: "A-42"
    cooled: true
```

```python
cfg = NavDict.from_yaml_file("setup.yaml")
detector = cfg.devices.detector
```

For `factory//`, navdict performs:

1. `DetectorFactory()`
2. `.create(**detector_args)`

## `int_enum//`: create an `IntEnum` dynamically

```yaml
ccd_sides:
  enum: int_enum//Side
  content:
    E:
      alias: [E_SIDE, RIGHT_SIDE]
      value: 1
    F:
      alias: [F_SIDE, LEFT_SIDE]
      value: 0
```

```python
cfg = NavDict.from_yaml_file("setup.yaml")
assert cfg.ccd_sides.enum.RIGHT_SIDE.value == 1
assert cfg.ccd_sides.enum.LEFT_SIDE.value == 0
```

## `env//`: read an environment variable

```yaml
auth:
  token: env//AUTH_TOKEN
```

```python
cfg = NavDict.from_yaml_string("""
auth:
  token: env//AUTH_TOKEN
""")

print(cfg.auth.token)
```

If the variable is not set, the result is `None`.

Because plugin-based directives are memoized, if the environment value changes
and you want to re-read it, reset memoization for that key:

```python
cfg.auth.del_memoized_key("token")
```

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

## Environment variable expansion in file directives

`ENV[VARNAME]` references in resource paths are supported for both `csv//` and
`yaml//` by default.

Equivalent syntax forms:

- `ENV[DATA_ROOT]`
- `ENV['DATA_ROOT']`
- `ENV["DATA_ROOT"]`

Example with `csv//`:

```yaml
setup:
  hk_metrics: csv//ENV[DATA_STORAGE]/hk_metrics_daq.csv
```

Example with `yaml//`:

```yaml
setup:
  camera: yaml//ENV[CONFIG_ROOT]/camera.yaml
```

If `DATA_STORAGE` is unset, navdict raises a `ValueError`.

Disable environment expansion when needed:

```yaml
setup:
  hk_metrics: csv//ENV[DATA_STORAGE]/hk_metrics_daq.csv
  hk_metrics_kwargs:
    expand_env: false
```

And similarly for YAML:

```yaml
setup:
  camera: yaml//ENV[CONFIG_ROOT]/camera.yaml
  camera_kwargs:
    expand_env: false
```

## Next

For directive plugin implementation details, see
[Developer Guide: Directive Plugins](../developer-guide/directive-plugins.md).
