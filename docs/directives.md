---
hide:
    - toc
---

# How directives work

## What are directives?

Directives are _instructions_ in a YAML file that are interpreted by the 
`NavigableDict` whenever the value containing the directive is accessed. 
Let's explain this with an example. We have a simple YAML file (`setup.yaml) 
with the following content:

```yaml
Setup:
    project_info: yaml//project_info.yaml
```
This short YAML string contains a directive `yaml//` which will load the 
`project_info.yaml` file whenever the `project_info` key is accessed. 

The `project_info.yaml` file contains the following keys:

```yaml
project: navdict
version: 0.3.2
```
Assume both YAML files are located in your HOME folder.

```
>>> from navdict import NavDict

>>> setup = NavDict.from_yaml_file("~/setup.yaml")
>>> print(setup)
Setup:
    project_info: yaml//project_info.yaml
>>> print(setup.Setup)
project_info: yaml//project_info.yaml
>>> print(setup.Setup.project_info)
project: navdict
version: 0.3.2
```

## Matching directives

A value containing a directive shall match against the following regular 
expression:

The value is a string matching `r"^([a-zA-Z]\w+)[\/]{2}(.*)$"` where:

- group 1 is the directive key and 
- group 2 is the directive value that is passed into the function that is 
  associated with the directive.

For example, the value 'yaml//config.yaml' will match and group 1 is 'yaml' 
and group 2 is 'config.yaml'.

The function `unravel_directive(...) -> tuple[str, str]` parses the 
directive and returns the two groups as a tuple. This happens under the hood 
and should not bother you unless you are a navdict developer 🧐

## Default directives

The `navdict` project has defined the following directives:

* `class//`: instantiate the class and return the object
* `factory//`: instantiates a factory and executes its `create()` method
* `csv//`: load the CSV file and return a list of lists of strings
* `yaml//`: load the YAML file and return a dictionary
* `int-enum//`: dynamically create the enumeration and return the Enum object
* `env//`: returns the value of the environment variable or None

## Filenames

When the directive value is a filename or path, it can be absolute or 
relative. An absolute filename is used as-is and passed to the directive 
function. A relative filename is interpreted as follows:

- when the parent —which should be a NavDict— contains a `_filename` 
  attribute, the value of the directive is interpreted relative to the 
  location of the parent.
- when the parent doesn't have a `_filename` attribute or if it is `None`, 
  then,
    - if the `NAVDICT_DEFAULT_RESOURCE_LOCATION` is defined, that location is 
      used, otherwise
    - the directive value is relative to the current working directory.

## Custom directives

If you have special needs to handle directives in your YAML files, you can 
implement your own directive as a plugin. What you need is a unique name for 
the directive and a function to handle and process the data.

The builtin directives `yaml//`, `csv//` and `env//` are implemented as a plugin 
and 
can serve as an example for your directive plugin.

In the `pyproject.toml` file of your project, you should add an entrypoint 
for your directive plugin. As an example, taken from the navdict project:

```toml
[project.entry-points."navdict.directive"]
yaml = 'navdict.directives:load_yaml'
csv = 'navdict.directives:load_csv'
env = 'navdict.directives:env_var'
```

The functions that you define to handle the directive shall have the 
following interface definition. The example is from the builtin `yaml` 
directive.

```python
def load_yaml(value: str, parent_location: Path | None, *args, **kwargs):
    ...
```

The `value` is the part of the directive that comes after the double slashes 
'//'. This might be a filename or path, or any other string that your 
directive needs for processing. 

The `parent_location` is the location of the YAML file that was used to load 
the navdict. You can use this location to determine the full path of a 
resource that you need for processing the directive. For example, if the 
`value` contains a filename and a relative path, the `parent_location` can 
be used as the root for this relative path. The builtin directives use a 
function `get_resource_location(...)` to determine the full path of the 
resource to be loaded, e.g.

```python
from navdict.navdict import get_resource_location

yaml_location = get_resource_location(parent_location, relative_path)
```

The `args` and `kwargs` are entries from the YAML file that are passed into 
the directive function without processing. The `args` are determined from 
the YAML field `<key>_args` and the `kwargs` from `<key>_kwargs`. For 
example, the `csv` directive can take a keyword argument `header_rows` to 
parse and skip a number of rows in the CSV file. The YAML file would look 
something like this:

```yaml
setup:
    hk_metrics: csv//data/hk_metrics_daq.csv
    hk_metrics_kwargs:
        header_rows: 2
```

This will pass `header_rows=2` as a keyword argument into the `load_csv()` 
directive function.
