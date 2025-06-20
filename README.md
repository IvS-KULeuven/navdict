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

Always install packages into a virtual environment which you can create with
```shell
python3 -m venv .venv
```
or when you are already using `uv`:
```shell
uv venv --python 3.12
```

Then install the package in that environment:

```bash
source .venv/bin/activate
pip install navdict
```

or with `uv`, simply run the following, since `uv` will automatically use 
the environment.

```shell
uv pip install navdict
```

### Installation in a project

When you want to use `navdict` in a project you are developing, add the 
dependency to your `pyproject.toml` manually, or using `uv`

```shell
uv add navdict
```
