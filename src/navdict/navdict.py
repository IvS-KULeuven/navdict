"""
NavDict: A navigable dictionary with dot notation access and automatic file loading.

NavDict extends Python's built-in dictionary to support convenient dot notation
access (data.user.name) alongside traditional key access (data["user"]["name"]).
It automatically loads data files and can instantiate classes dynamically based
on configuration.

Features:
    - Dot notation access for nested data structures
    - Automatic file loading (CSV, YAML, JSON, etc.)
    - Dynamic class instantiation from configuration
    - Full backward compatibility with standard dictionaries

Example:
    >>> from navdict import navdict
    >>> data = navdict({"user": {"name": "Alice", "config_file": "yaml//settings.yaml"}})
    >>> data.user.name              # "Alice"
    >>> data.user.config_file       # Automatically loads and parses settings.yaml
    >>> data["user"]["name"]        # Still works with traditional access

Author: Rik Huygen
License: MIT
"""

from __future__ import annotations

__all__ = [
    "navdict",  # noqa: ignore typo
    "NavDict",
]

import csv
import datetime
import enum
import importlib
import logging
import textwrap
import warnings
from enum import Enum
from pathlib import Path
from typing import Any
from typing import Type
from typing import Union

from _ruamel_yaml import ScannerError
from rich.text import Text
from rich.tree import Tree
from ruamel.yaml import YAML

logger = logging.getLogger("navdict")


def _load_directive_plugins():
    """
    Load any directive plugins that are available in your environment.
    """


def _load_class(class_name: str):
    """
    Find and returns a class based on the fully qualified name.

    A class name can be preceded with the string `class//` or `factory//`. This is used in YAML
    files where the class is then instantiated on load.

    Args:
        class_name (str): a fully qualified name for the class
    """
    if class_name.startswith("class//"):
        class_name = class_name[7:]
    elif class_name.startswith("factory//"):
        class_name = class_name[9:]

    module_name, class_name = class_name.rsplit(".", 1)
    module = importlib.import_module(module_name)
    return getattr(module, class_name)


def _get_resource_location(parent: NavigableDict, in_dir: str) -> Path:
    """
    Returns the resource location.

    The resource location is the path to the file that is provided in a directive
    such as `yaml//` or `csv//`. The location of the file can be given as an absolute
    path or can be relative in which case there are two possibilities:

    1. the parent NavDict exists and has a `_filename` attribute that is not None. In
       this case the resource location will be relative to the parent's location.
    2. the parent is not given, or it has no `_filename` attribute, or it's `_filename`
       attribute is None. In this case the resource location is taken to be relative
       to the current working directory '.'.

    Args:
        parent: the parent NavDict of this key-value pair, or None
        in_dir: a location extracted from the directive's value.

    Returns:
        A Path object with the resource location.

    """

    def get_default_location() -> Path:

        if parent and (resource_location := parent.get_private_attribute("_filename")):
            return resource_location.parent

        return Path('.').expanduser()

    match in_dir:
        case str() if Path(in_dir).is_absolute():
            location = Path(in_dir)
        case None:
            location = get_default_location()
        case _:
            location = get_default_location() / in_dir

    # logger.debug(f"{location=}, {fn=}")

    return location


def _load_csv(resource_name: str, *args, parent: navdict = None, **kwargs):
    """Find and return the content of a CSV file."""

    # logger.debug(f"{resource_name=}, {parent=}")

    if resource_name.startswith("csv//"):
        resource_name = resource_name[5:]

    parts = resource_name.rsplit("/", 1)
    in_dir, fn = parts if len(parts) > 1 else [None, parts[0]]

    try:
        n_header_rows = int(kwargs["header_rows"])
    except KeyError:
        n_header_rows = 0

    csv_location = _get_resource_location(parent, in_dir)

    try:
        with open(csv_location / fn, 'r', encoding='utf-8') as file:
            csv_reader = csv.reader(file)
            data = list(csv_reader)
    except FileNotFoundError:
        logger.error(f"Couldn't load resource '{resource_name}', file not found", exc_info=True)
        raise

    return data[:n_header_rows], data[n_header_rows:]


def _load_int_enum(enum_name: str, enum_content) -> Type[Enum]:
    """Dynamically build (and return) and IntEnum.

    In the YAML file this will look like below.
    The IntEnum directive (where <name> is the class name):

        enum: int_enum//<name>

    The IntEnum content:

        content:
            E:
                alias: ['E_SIDE', 'RIGHT_SIDE']
                value: 1
            F:
                alias: ['F_SIDE', 'LEFT_SIDE']
                value: 0

    Args:
        - enum_name: Enumeration name (potentially prepended with "int_enum//").
        - enum_content: Content of the enumeration, as read from the navdict field.
    """
    if enum_name.startswith("int_enum//"):
        enum_name = enum_name[10:]

    definition = {}
    for side_name, side_definition in enum_content.items():
        if "alias" in side_definition:
            aliases = side_definition["alias"]
        else:
            aliases = []
        value = side_definition["value"]

        definition[side_name] = value

        for alias in aliases:
            definition[alias] = value

    return enum.IntEnum(enum_name, definition)


def _load_yaml(resource_name: str, parent: NavDict = None) -> NavDict:
    """Find and return the content of a YAML file."""

    # logger.debug(f"{resource_name=}, {parent=}")

    if resource_name.startswith("yaml//"):
        resource_name = resource_name[6:]

    parts = resource_name.rsplit("/", 1)

    in_dir, fn = parts if len(parts) > 1 else [None, parts[0]]

    yaml_location = _get_resource_location(parent, in_dir)

    try:
        yaml = YAML(typ='safe')
        with open(yaml_location / fn, 'r') as file:
            data = yaml.load(file)

    except FileNotFoundError:
        logger.error(f"Couldn't load resource '{resource_name}', file not found", exc_info=True)
        raise
    except IsADirectoryError:
        logger.error(f"Couldn't load resource '{resource_name}', file seems to be a directory", exc_info=True)
        raise

    data = NavigableDict(data, _filename=yaml_location / fn)

    # logger.debug(f"{data.get_private_attribute('_filename')=}")

    return data


def _get_attribute(self, name, default):
    try:
        attr = object.__getattribute__(self, name)
    except AttributeError:
        attr = default
    return attr


class NavigableDict(dict):
    """
    A NavigableDict is a dictionary where all keys in the original dictionary are also accessible
    as attributes to the class instance. So, if the original dictionary (setup) has a key
    "site_id" which is accessible as `setup['site_id']`, it will also be accessible as
    `setup.site_id`.

    Args:
        head (dict): the original dictionary
        label (str): a label or name that is used when printing the navdict

    Examples:
        >>> setup = NavigableDict({'site_id': 'KU Leuven', 'version': "0.1.0"})
        >>> assert setup['site_id'] == setup.site_id
        >>> assert setup['version'] == setup.version

    Note:
        We always want **all** keys to be accessible as attributes, or none. That means all
        keys of the original dictionary shall be of type `str`.

    """

    def __init__(self, head: dict = None, label: str = None, _filename: str = None):

        head = head or {}
        super().__init__(head)
        self.__dict__["_memoized"] = {}
        self.__dict__["_label"] = label
        self.__dict__["_filename"] = _filename

        # By agreement, we only want the keys to be set as attributes if all keys are strings.
        # That way we enforce that always all keys are navigable, or none.

        if any(True for k in head.keys() if not isinstance(k, str)):
            # invalid_keys = list(k for k in head.keys() if not isinstance(k, str))
            # logger.warning(f"Dictionary will not be dot-navigable, not all keys are strings [{invalid_keys=}].")
            return

        for key, value in head.items():
            if isinstance(value, dict):
                value = NavigableDict(head.__getitem__(key), _filename=_filename)
                setattr(self, key, value)
            else:
                setattr(self, key, head.__getitem__(key))

    @property
    def label(self) -> str | None:
        return self._label

    def add(self, key: str, value: Any):
        """Set a value for the given key.

        If the value is a dictionary, it will be converted into a NavigableDict and the keys
        will become available as attributes provided that all the keys are strings.

        Args:
            key (str): the name of the key / attribute to access the value
            value (Any): the value to assign to the key
        """
        if isinstance(value, dict) and not isinstance(value, NavigableDict):
            value = NavigableDict(value)
        setattr(self, key, value)

    def clear(self) -> None:
        for key in list(self.keys()):
            self.__delitem__(key)

    def __repr__(self):
        return f"{self.__class__.__name__}({super()!r}) [id={id(self)}]"

    def __delitem__(self, key):
        dict.__delitem__(self, key)
        object.__delattr__(self, key)

    def __setattr__(self, key, value):
        # logger.info(f"called __setattr__({self!r}, {key}, {value})")
        if isinstance(value, dict) and not isinstance(value, NavigableDict):
            value = NavigableDict(value)
        self.__dict__[key] = value
        super().__setitem__(key, value)
        try:
            del self.__dict__["_memoized"][key]
        except KeyError:
            pass

    # This method is called:
    #   - for *every* single attribute access on an object using dot notation.
    #   - when using the `getattr(obj, 'name') function
    #   - accessing any kind of attributes, e.g. instance or class variables,
    #     methods, properties, dunder methods, ...
    #
    # Note: `__getattr__` is only called when an attribute cannot be found
    #       through normal means.
    def __getattribute__(self, key):
        # logger.info(f"called __getattribute__({key})")
        value = object.__getattribute__(self, key)
        if key.startswith('__'):  # small optimization
            return value
        # We can not directly call the `_handle_directive` function here due to infinite recursion
        m = object.__getattribute__(self, "_handle_directive")
        return m(key, value)

    def __delattr__(self, item):
        # logger.info(f"called __delattr__({self!r}, {item})")
        object.__delattr__(self, item)
        dict.__delitem__(self, item)

    def __setitem__(self, key, value):
        # logger.debug(f"called __setitem__({self!r}, {key}, {value})")
        if isinstance(value, dict) and not isinstance(value, NavigableDict):
            value = NavigableDict(value)
        super().__setitem__(key, value)
        self.__dict__[key] = value
        try:
            del self.__dict__["_memoized"][key]
        except KeyError:
            pass

    # This method is called:
    #   - whenever square brackets `[]` are used on an object, e.g. indexing or slicing.
    #   - during iteration, if an object doesn't have __iter__ defined, Python will try
    #     to iterate using __getitem__ with successive integer indices starting from 0.
    def __getitem__(self, key):
        # logger.info(f"called __getitem__({self!r}, {key})")
        value = super().__getitem__(key)
        if key.startswith('__'):
            return value
        # no danger for recursion here, so we can directly call the function
        return self._handle_directive(key, value)

    def _handle_directive(self, key, value) -> Any:
        """
        This method will handle the available directives. This may be builtin directives
        like `class/` or `yaml//`, or it may be external directives that were provided
        as a plugin. TO BE IMPLEMENTED

        Args:
            key: the key of the field that might contain a directive
            value: the value which might be a directive

        Returns:
            This function will return the value, either the original value or the result of
                evaluating and executing a directive.
        """
        # logger.debug(f"called _handle_directive({key}, {value!r}) [id={id(self)}]")
        if isinstance(value, str) and value.startswith("class//"):
            args, kwargs = self._get_args_and_kwargs(key)
            return _load_class(value)(*args, **kwargs)

        elif isinstance(value, str) and value.startswith("factory//"):
            factory_args = _get_attribute(self, f"{key}_args", {})
            return _load_class(value)().create(**factory_args)

        elif isinstance(value, str) and value.startswith("yaml//"):
            if key in self.__dict__["_memoized"]:
                return self.__dict__["_memoized"][key]
            content = _load_yaml(value, parent=self)
            self.__dict__["_memoized"][key] = content
            return content

        elif isinstance(value, str) and value.startswith("csv//"):
            if key in self.__dict__["_memoized"]:
                return self.__dict__["_memoized"][key]
            args, kwargs = self._get_args_and_kwargs(key)
            content = _load_csv(value, parent=self, **kwargs)
            self.__dict__["_memoized"][key] = content
            return content

        elif isinstance(value, str) and value.startswith("int_enum//"):
            content = object.__getattribute__(self, "content")
            return _load_int_enum(value, content)

        else:
            return value

    def _get_args_and_kwargs(self, key):
        """
        Read the args and kwargs that are associated with the key of a directive.

        An example of such a directive:

          hexapod:
              device: class//egse.hexapod.PunaProxy
              device_args: [PUNA_01]
              device_kwargs:
                  sim: true

        There might not be any positional nor keyword arguments provided in which
        case and empty tuple and/or dictionary is returned.

        Returns:
            A tuple containing any positional arguments and a dictionary containing
                keyword arguments.
        """
        try:
            args = object.__getattribute__(self, f"{key}_args")
        except AttributeError:
            args = ()
        try:
            kwargs = object.__getattribute__(self, f"{key}_kwargs")
        except AttributeError:
            kwargs = {}

        return args, kwargs

    def set_private_attribute(self, key: str, value: Any) -> None:
        """Sets a private attribute for this object.

        The name in key will be accessible as an attribute for this object, but the key will not
        be added to the dictionary and not be returned by methods like keys().

        The idea behind this private attribute is to have the possibility to add status information
        or identifiers to this classes object that can be used by save() or load() methods.

        Args:
            key (str): the name of the private attribute (must start with an underscore character).
            value: the value for this private attribute

        Examples:
            >>> setup = NavigableDict({'a': 1, 'b': 2, 'c': 3})
            >>> setup.set_private_attribute("_loaded_from_dict", True)
            >>> assert "c" in setup
            >>> assert "_loaded_from_dict" not in setup
            >>> assert setup.get_private_attribute("_loaded_from_dict") == True

        """
        if key in self:
            raise ValueError(f"Invalid argument key='{key}', this key already exists in the dictionary.")
        if not key.startswith("_"):
            raise ValueError(f"Invalid argument key='{key}', must start with underscore character '_'.")
        self.__dict__[key] = value

    def get_private_attribute(self, key: str) -> Any:
        """Returns the value of the given private attribute.

        Args:
            key (str): the name of the private attribute (must start with an underscore character).

        Returns:
            the value of the private attribute given in `key` or None if the attribute doesn't exist.

        Note:
            Because of the implementation, this private attribute can also be accessed as a 'normal'
            attribute of the object. This use is however discouraged as it will make your code less
            understandable. Use the methods to access these 'private' attributes.
        """
        if not key.startswith("_"):
            raise ValueError(f"Invalid argument key='{key}', must start with underscore character '_'.")
        try:
            return self.__dict__[key]
        except KeyError:
            return None

    def has_private_attribute(self, key):
        """
        Check if the given key is defined as a private attribute.

        Args:
            key (str): the name of a private attribute (must start with an underscore)
        Returns:
            True if the given key is a known private attribute.
        Raises:
            ValueError: when the key doesn't start with an underscore.
        """
        if not key.startswith("_"):
            raise ValueError(f"Invalid argument key='{key}', must start with underscore character '_'.")

        # logger.debug(f"{self.__dict__.keys()} for [id={id(self)}]")

        try:
            _ = self.__dict__[key]
            return True
        except KeyError:
            return False

    def get_raw_value(self, key):
        """
        Returns the raw value of the given key.

        Some keys have special values that are interpreted by the NavigableDict class. An example is
        a value that starts with 'class//'. When you access these values, they are first converted
        from their raw value into their expected value, e.g. the instantiated object in the above
        example. This method allows you to access the raw value before conversion.
        """
        try:
            return object.__getattribute__(self, key)
        except AttributeError:
            raise KeyError(f"The key '{key}' is not defined.")

    def __str__(self):
        return self._pretty_str()

    def _pretty_str(self, indent: int = 0):
        msg = ""

        for k, v in self.items():
            if isinstance(v, NavigableDict):
                msg += f"{'    ' * indent}{k}:\n"
                msg += v._pretty_str(indent + 1)
            else:
                msg += f"{'    ' * indent}{k}: {v}\n"

        return msg

    def __rich__(self) -> Tree:
        tree = Tree(self.__dict__["_label"] or "NavigableDict", guide_style="dim")
        _walk_dict_tree(self, tree, text_style="dark grey")
        return tree

    def _save(self, fd, indent: int = 0):
        """
        Recursive method to write the dictionary to the file descriptor.

        Indentation is done in steps of four spaces, i.e. `'    '*indent`.

        Args:
            fd: a file descriptor as returned by the open() function
            indent (int): indentation level of each line [default = 0]

        """

        # Note that the .items() method returns the actual values of the keys and doesn't use the
        # __getattribute__ or __getitem__ methods. So the raw value is returned and not the
        # _processed_ value.

        for k, v in self.items():
            # history shall be saved last, skip it for now

            if k == "history":
                continue

            # make sure to escape a colon in the key name

            if isinstance(k, str) and ":" in k:
                k = '"' + k + '"'

            if isinstance(v, NavigableDict):
                fd.write(f"{'    ' * indent}{k}:\n")
                v._save(fd, indent + 1)
                fd.flush()
                continue

            if isinstance(v, float):
                v = f"{v:.6E}"
            fd.write(f"{'    ' * indent}{k}: {v}\n")
            fd.flush()

        # now save the history as the last item

        if "history" in self:
            fd.write(f"{'    ' * indent}history:\n")
            self.history._save(fd, indent + 1)  # noqa

    def get_memoized_keys(self):
        return list(self.__dict__["_memoized"].keys())

    @staticmethod
    def from_dict(my_dict: dict, label: str = None) -> NavigableDict:
        """Create a NavigableDict from a given dictionary.

        Remember that all keys in the given dictionary shall be of type 'str' in order to be
        accessible as attributes.

        Args:
            my_dict: a Python dictionary
            label: a label that will be attached to this navdict

        Examples:
            >>> setup = navdict.from_dict({"ID": "my-setup-001", "version": "0.1.0"}, label="Setup")
            >>> assert setup["ID"] == setup.ID == "my-setup-001"

        """
        return NavigableDict(my_dict, label=label)

    @staticmethod
    def from_yaml_string(yaml_content: str = None, label: str = None) -> NavigableDict:
        """Creates a NavigableDict from the given YAML string.

        This method is mainly used for easy creation of a navdict from strings during unit tests.

        Args:
            yaml_content: a string containing YAML
            label: a label that will be attached to this navdict

        Returns:
            a navdict that was loaded from the content of the given string.
        """

        if not yaml_content:
            raise ValueError("Invalid argument to function: No input string or None given.")

        yaml = YAML(typ='safe')
        try:
            data = yaml.load(yaml_content)
        except ScannerError as exc:
            raise ValueError(f"Invalid YAML string: {exc}")

        return NavigableDict(data, label=label)

    @staticmethod
    def from_yaml_file(filename: Union[str, Path] = None) -> NavigableDict:
        """Creates a navigable dictionary from the given YAML file.

        Args:
            filename (str): the path of the YAML file to be loaded

        Returns:
            a navdict that was loaded from the given location.

        Raises:
            ValueError: when no filename is given.
        """

        if not filename:
            raise ValueError("Invalid argument to function: No filename or None given.")

        data = _load_yaml(str(filename))

        if data == {}:
            warnings.warn(f"Empty YAML file: {filename!s}")

        return data

    def to_yaml_file(self, filename: str | Path = None) -> None:
        """Saves a NavigableDict to a YAML file.

        When no filename is provided, this method will look for a 'private' attribute
        `_filename` and use that to save the data.

        Args:
            filename (str|Path): the path of the YAML file where to save the data

        Note:
            This method will **overwrite** the original or given YAML file and therefore you might
            lose proper formatting and/or comments.

        """
        if not filename:
            try:
                filename = self.get_private_attribute("_filename")
            except KeyError:
                raise ValueError("No filename given or known, can not save navdict.")

        with Path(filename).open("w") as fd:
            fd.write(
                textwrap.dedent(
                    f"""
                    # This YAML file is generated by:
                    #
                    #    Setup.to_yaml_file(setup, filename="{filename}')
                    #
                    # Created on {datetime.datetime.now(tz=datetime.timezone.utc).isoformat()}
                    
                    """
                )
            )

            self._save(fd, indent=0)

        self.set_private_attribute("_filename", Path(filename))

    def get_filename(self) -> str | None:
        """Returns the filename for this navdict or None when no filename could be determined."""
        return self.get_private_attribute("_filename")


navdict = NavDict = NavigableDict  # noqa: ignore typo
"""Shortcuts for NavigableDict and more Pythonic."""


def _walk_dict_tree(dictionary: dict, tree: Tree, text_style: str = "green"):
    for k, v in dictionary.items():
        if isinstance(v, dict):
            branch = tree.add(f"[purple]{k}", style="", guide_style="dim")
            _walk_dict_tree(v, branch, text_style=text_style)
        else:
            text = Text.assemble((str(k), "medium_purple1"), ": ", (str(v), text_style))
            tree.add(text)
