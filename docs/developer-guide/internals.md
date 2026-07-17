# Internals

## Data model

`NavigableDict` stores data as dictionary keys while mirroring keys as
attributes for dot navigation.

## Lazy directive resolution

When reading a value by key or attribute, navdict checks whether the stored
value is a directive string and resolves it only on access.

## Memoization

Resolved directive values are memoized per key so repeated access does not
recompute by default.

Inspect and manage memoized directive keys with:

- `get_memoized_keys()`
- `del_memoized_key(key)`

Example:

```python
import os

from navdict import NavDict

cfg = NavDict.from_yaml_string("""
config:
	token: env//AUTH_TOKEN
""")

os.environ["AUTH_TOKEN"] = "token-v1"
assert cfg.config.token == "token-v1"
assert cfg.config.get_memoized_keys() == ["token"]

os.environ["AUTH_TOKEN"] = "token-v2"

# Still returns memoized value unless cache is reset.
assert cfg.config.token == "token-v1"

cfg.config.del_memoized_key("token")
assert cfg.config.token == "token-v2"
```

Notes:

- Memoization applies to plugin-backed directives.
- Keys are memoized only after first access.
- `del_memoized_key` returns `False` when the key is not currently memoized.

## Resource location

For file-based directives, navdict resolves paths using source file context
first, then `NAVDICT_DEFAULT_RESOURCE_LOCATION`, then current working
directory.

## Alias hook

When normal lookup fails, an optional alias hook can map an alias to a real
key and retry lookup.
