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
