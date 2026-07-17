# Getting Started

This guide gets you from installation to your first practical `navdict` usage
in a few minutes.

## Install

Use your preferred environment workflow.

```shell
uv add navdict
```

Or with pip in a virtual environment:

```shell
python3 -m venv .venv
source .venv/bin/activate
pip install navdict
```

## Create your first navdict

```python
from navdict import NavDict

config = NavDict(
    {
        "instrument": {
            "name": "NIR-1",
            "camera": {
                "gain": 1.5,
                "offset": 100,
            },
        }
    }
)

# Dictionary style
print(config["instrument"]["camera"]["gain"])

# Dot notation style
print(config.instrument.camera.gain)
```

Both access styles return the same values.

## Discover available keys

When navigating nested structures, `keys()` helps you discover what is
available at each level.

```python
print(config.instrument.keys())
# dict_keys(['name', 'camera'])

print(config.instrument.camera.keys())
# dict_keys(['gain', 'offset'])
```

## Pretty-print a navdict

For a full readable view of a nested structure, use `rich.print`.

```python
from rich import print

print(config)
```

Example output:

```text
NavigableDict
└── instrument
    ├── name: NIR-1
    └── camera
        ├── gain: 1.5
        └── offset: 100
```

Be aware that printing a large configuration can produce a lot of output.

## Add a label

You can attach a label when creating a navdict. The label is mainly used as the
root title in rich tree output.

```python
from navdict import NavDict
from rich import print

config = NavDict(
    {
        "instrument": {
            "name": "NIR-1",
        }
    },
    label="Instrument Config",
)

print(config)
```

Example output:

```text
Instrument Config
└── instrument
    └── name: NIR-1
```

You can also set or change the label later:

```python
config.set_label("Setup")
print(config.get_label())
# Setup
```

Notes:

- Labels can be passed through `NavDict(...)`, `NavDict.from_dict(...)`, and
  `NavDict.from_yaml_string(...)`.
- `from_yaml_file(...)` does not accept a `label` argument.

## Load from YAML

When your configuration lives in files, load it directly:

```python
from navdict import NavDict

setup = NavDict.from_yaml_file("setup.yaml")
print(setup.instrument.name)
```

## Use a directive

Directives are values with the format `<name>//<value>`. They are resolved when
accessed.

Example YAML:

```yaml
instrument:
  calibration: csv//calibration.csv
```

Example Python:

```python
from navdict import NavDict

setup = NavDict.from_yaml_file("setup.yaml")
coefficients = setup.instrument.calibration
```

Common built-in directives include:

- `yaml//`: load nested YAML
- `csv//`: load CSV resources
- `class//`: instantiate a class
- `factory//`: instantiate a factory and call `create()`
- `int-enum//`: build an enum dynamically
- `env//`: read an environment variable

## Where to go next

- Learn directive usage in [User Guide: Directives](user-guide/directives.md)
- Learn alternative key naming in [User Guide: Aliases](user-guide/aliases.md)
- Learn plugin extension in [Developer Guide: Directive Plugins](developer-guide/directive-plugins.md)
