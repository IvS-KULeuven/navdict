# Recipes

## Use navdict as an application config object

```python
from navdict import NavDict

cfg = NavDict.from_yaml_file("app.yaml")
if cfg.database.enabled:
    connect(cfg.database.url)
```

## Keep large data outside main config

```yaml
pipeline:
  calibration: csv//data/calibration.csv
```

This keeps config readable while loading data lazily.

## Add optional environment-dependent paths

```yaml
storage:
  index: csv//ENV[DATA_ROOT]/index.csv
```

Set `DATA_ROOT` per environment to reuse the same config.

## Use aliases to support multiple naming conventions

Define an alias map when users and code use different names for the same key.

## Avoid mixed key types at one level

Dot navigation is enabled per dictionary level only when all keys at that level
are strings.

If one key is non-string, attribute access is disabled for all keys at that
level to avoid partial and confusing behavior.

```python
from navdict import NavDict

data = NavDict(
  {
    "root": {
      "valid": "A",
      1: "one",
    }
  }
)

# Dictionary access still works.
print(data.root["valid"])
print(data.root[1])

# Attribute access at this level is not available.
# print(data.root.valid)
```

Recommendation: keep keys as strings for levels where dot navigation is used.
