# Aliases

Aliases let you refer to the same value with multiple names.

This is useful when users or systems use different terms for the same field.

## How alias resolution works

A navdict instance can define one alias hook function with
`set_alias_hook(...)`.

The hook receives the missing name and must return the real key.

## Example

```yaml
House:
  Cameras:
    cam_1:
      location: front door
      type: XYZ-A123
    cam_2:
      location: front garage
      type: XYZ-B123
```

```python
from navdict import navdict

iot = navdict.from_yaml_file("cameras.yaml")
print(iot.House.Cameras.cam_1.type)


def abbrev(name: str) -> str:
    aliases = {
        "front_door": "cam_1",
        "front_garage": "cam_2",
    }
    return aliases[name]


iot.House.Cameras.set_alias_hook(abbrev)
print(iot.House.Cameras.front_door.type)
```
