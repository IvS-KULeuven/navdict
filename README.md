# NavigableDict (aka. navdict)

A Python dictionary that supports both traditional key access (`dict["key"]`)
and convenient dot notation (`dict.key`) for navigating nested data 
structures, plus some extras.

## Features

- **Dot Notation Access**: Access nested dictionaries with `data.user.name` instead of `data["user"]["name"]`
- **Backward Compatible**: Works exactly like a regular dictionary for all standard operations
- **Nested Structure Support**: Automatically converts nested dictionaries to navdict objects
- **Safe Attribute Access**: Handles keys that conflict with dictionary methods gracefully
- **Type Hints**: Full typing support for better IDE integration
- **Lightweight**: Minimal overhead over standard dictionaries

and 

- **Automatic File Loading**: Seamlessly load and parse data files (CSV, YAML, JSON, etc.) when accessing dictionary keys, eliminating manual file handling
- **Dynamic Class Instantiation**: Automatically import and instantiate classes with configurable parameters, enabling flexible object creation from configuration data


## Installation

### From PyPI (Recommended)

```bash
pip install navdict
```
