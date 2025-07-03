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

- group 1 is the directive and 
- group 2 is the value that is passed into the function that is associated 
  with the directive.

For example, the value 'yaml//config.yaml' will match and group 1 is 'yaml' 
and group 2 is 'config.yaml'.


## Default directives

The `navdict` project has defined the following directives:

* `class//`: instantiate the class and return the object
* `factory//`: instantiates a factory and executes its `create()` method
* `csv//`: load the CSV file and return a numpy array
* `yaml//`: load the YAML file and return a dictionary
* `int-enum//`: dynamically create the enumeration and return the Enum object

## Filenames

When the directive value is a filename or path, it can be absolute or 
relative. An absolute filename is used as-is and passed to the directive 
function. A relative filename is interpreted as follows:

- when the parent —which should be a NavDict— contains a `_filename` 
  attribute, the value of the directive is interpreted relative to the 
  location of the parent.
- when the parent doesn't have a `_filename` attribute or if it is `None`, 
  the directive value is relative to the current working directory.

## Custom directives

TBW. This section will describe how to write your own directives as a plugin.
