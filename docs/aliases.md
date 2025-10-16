---
hide:
    - toc
---

# Aliases

Sometimes we might want to refer to the same value in a dictionary with different keys or attributes. For example, 
in a configuration of a test setup, the same device might have different or abbreviated names to refer to the same 
item. That is where we can use aliases.

For every NavDict we can define one alias hook function that maps aliases to a valid attribute or key. The hook 
function shall take one argument, which is the alias, and returns the valid key for the navdict.

An example might make things clearer. Suppose we have a setup that defines a number of cameras in our house. The 
cameras might be referred with their identifiers as follows:

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

When this YAML file is read into a navdict, it will look like this:

```
iot = navdict.from_yaml_file("cameras.yaml")
print(iot.House.Cameras.cam_1.type)
XYZ-A123
```
If we now write a function that translate proper names into the correct camera id:

```python
def abbrev(name: str) -> str:
    aliases = {
        "front_door": "cam_1",
        "front_garage": "cam_2"
    }
    return aliases[name]

iot.House.Cameras.set_alias_hook(abbrev)
```
We can now refer to the cameras with their proper names:
```
iot.House.Cameras.front_door.type
XYZ-A123
```
