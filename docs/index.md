# An intelligent navigable dictionary


🚧– WIP – this is an early version of a project in development. Please use it 
and fork it and create issues and feature requests.

This module defines the NavigableDict (aka. `navdict`), which is a dictionary
that is dot-navigable and has some special features to autoload files.

The information that is in the NavigableDict can be navigated in two different
ways. First, the navdict is a dictionary, so all information can be accessed by
keys as in the following example.

    >>> setup = NavigableDict({"gse": {"hexapod": {"ID": 42, "calibration": [0,1,2,3,4,5]}}})
    >>> setup["gse"]["hexapod"]["ID"]
    42

Second, each of the _keys_ is also available as an attribute of the
NavigableDict and that makes it possible to navigate the navdict with
dot-notation:

    >>> id = setup.gse.hexapod.ID

If you want to know which keys you can use to navigate the navdict, use
the `keys()` method.

    >>> setup.gse.hexapod.keys()
    dict_keys(['ID', 'calibration'])
    >>> setup.gse.hexapod.calibration
    [0, 1, 2, 3, 4, 5]

To get a full printout of the navdict, you can use the print method from the
rich package. Be careful, because this can print out a lot of information when a
full configuration is loaded.

    >>> from rich import print
    >>> print(setup)
    NavigableDict
    └── gse
        └── hexapod
            ├── ID: 42
            └── calibration: [0, 1, 2, 3, 4, 5]

### Special Values

Some of the information in the navdict is interpreted in a special way, i.e.
some values are processed before returning. Examples are the classes and
calibration/data files. The following values are treated special if they start
with:

* `class//`: instantiate the class and return the object
* `factory//`: instantiates a factory and executes its `create()` method
* `csv//`: load the CSV file and return a list of lists of strings
* `yaml//`: load the YAML file and return a dictionary
* `int-enum//`: dynamically create the enumeration and return the Enum object

We call these values _directives_ and they are explained in more detail in 
[How directives work](./directives.md).

#### Data Files

Some information is too large to add to the navdict as such and should be loaded
from a data file. Examples are calibration files, flat-fields, temperature
conversion curves, etc.

The navdict will automatically load the file when you access a key that 
contains a value that starts with `csv//` or `yaml//`.

    >>> setup = navdict({
    ...     "instrument": {"coeff": "csv//cal_coeff_1234.csv"}
    ... })
    >>> setup.instrument.coeff[0, 4]
    5.0

Note: the resource location is always relative to the current location XXXX 
