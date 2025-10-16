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
    "NavigableDict",
    "get_resource_location",
]

import csv
import datetime
import importlib
import itertools
import logging
import os
import textwrap
import warnings
from enum import IntEnum
from pathlib import Path
from typing import Any
from typing import Callable

from rich.text import Text
from rich.tree import Tree
from ruamel.yaml import YAML
from ruamel.yaml.scanner import ScannerError

from navdict.directive import is_directive
from navdict.directive import unravel_directive
from navdict.directive import get_directive_plugin

logger = logging.getLogger("navdict")


def load_class(class_name: str):
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


def get_resource_location(parent_location: Path | None, in_dir: str | None) -> Path:
    """
    Returns the resource location.

    The resource location is the path to the file that is provided in a directive
    such as `yaml//` or `csv//`. The location of the file can be given as an absolute
    path or can be relative in which case there are two possibilities:

    1. the parent location is not None.
       In this case the resource location will be relative to the parent's location.
    2. the parent location is None.
       In this case the resource location is taken to be relative to the current working directory '.'
       unless the environment variable NAVDICT_DEFAULT_RESOURCE_LOCATION is provided in which case
       it is taken from that variable.
    3. when both arguments are None, the resource location will be the current working directory '.'
       unless the environment variable NAVDICT_DEFAULT_RESOURCE_LOCATION is provided in which case
       it is taken from that variable.

    Args:
        parent_location: the location of the parent navdict, or None
        in_dir: a location extracted from the directive's value.

    Returns:
        A Path object with the resource location.

    """

    match (parent_location, in_dir):
        case (_, str()) if Path(in_dir).is_absolute():
            location = Path(in_dir)
        case (None, str()):
            location = Path(os.getenv("NAVDICT_DEFAULT_RESOURCE_LOCATION", ".")) / in_dir
        case (Path(), str()):
            location = parent_location / in_dir
        case (Path(), None):
            location = parent_location
        case _:
            location = Path(os.getenv("NAVDICT_DEFAULT_RESOURCE_LOCATION", "."))

    # logger.debug(f"{location=}, {fn=}")

    return location


def load_csv(resource_name: str, parent_location: Path | None, *args, **kwargs) -> list[list[str]]:
    """
    Find and return the content of a CSV file.

    If the `resource_name` argument starts with the directive (`csv//`), it will be split off automatically.
    The `kwargs` dictionary can contain the key `header_rows` which indicates the number of header rows to
    be skipped when processing the file.

    Returns:
        A list of the split lines, i.e. a list of lists of strings.
    """

    # logger.debug(f"{resource_name=}, {parent_location=}")

    if resource_name.startswith("csv//"):
        resource_name = resource_name[5:]

    if not resource_name:
        raise ValueError(f"Resource name should not be empty, but contain a valid filename.")

    parts = resource_name.rsplit("/", 1)
    in_dir, fn = parts if len(parts) > 1 else (None, parts[0])  # use a tuple here to make Mypy happy

    try:
        n_header_rows = int(kwargs["header_rows"])
    except KeyError:
        n_header_rows = 0

    csv_location = get_resource_location(parent_location, in_dir)

    def filter_lines(file_obj, n_skip):
        """
        Generator that filters out comment lines and skips header lines.
        The standard library csv module cannot handle this functionality.
        """

        for line in itertools.islice(file_obj, n_skip, None):
            if not line.strip().startswith("#"):
                yield line

    try:
        with open(csv_location / fn, "r", encoding="utf-8") as file:
            filtered_lines = filter_lines(file, n_header_rows)
            csv_reader = csv.reader(filtered_lines)
            data = list(csv_reader)
    except FileNotFoundError:
        logger.error(f"Couldn't load resource '{resource_name}', file not found", exc_info=True)
        raise

    return data


def load_int_enum(enum_name: str, enum_content) -> IntEnum:
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

    return IntEnum(enum_name, definition)


def load_yaml(resource_name: str, parent_location: Path | None = None, *args, **kwargs) -> NavigableDict:
    """Find and return the content of a YAML file."""

    # logger.debug(f"{resource_name=}, {parent_location=}")

    if resource_name.startswith("yaml//"):
        resource_name = resource_name[6:]

    parts = resource_name.rsplit("/", 1)

    in_dir, fn = parts if len(parts) > 1 else (None, parts[0])  # use a tuple here to make Mypy happy

    yaml_location = get_resource_location(parent_location, in_dir)

    try:
        yaml = YAML(typ="safe")
        with open(yaml_location / fn, "r") as file:
            data = yaml.load(file)

    except FileNotFoundError:
        logger.error(f"Couldn't load resource '{resource_name}', file not found", exc_info=True)
        raise
    except IsADirectoryError:
        logger.error(
            f"Couldn't load resource '{resource_name}', file seems to be a directory",
            exc_info=True,
        )
        raise
    except ScannerError as exc:
        msg = f"A error occurred while scanning the YAML file: {yaml_location / fn}."
        logger.error(msg, exc_info=True)
        raise IOError(msg) from exc

    data = NavigableDict(data, _filename=yaml_location / fn)

    # logger.debug(f"{data.get_private_attribute('_filename')=}")

    return data


def _get_attribute(self, name, default):
    """
    Safely retrieve an attribute from the object, returning a default if not found.

    This method uses object.__getattribute__() to bypass any custom __getattr__
    or __getattribute__ implementations on the class, accessing attributes directly
    from the object's internal dictionary.

    Args:
        name (str): The name of the attribute to retrieve.
        default: The value to return if the attribute does not exist.

    Returns:
        The attribute value if it exists, otherwise the default value.

    Note:
        This is typically used internally to avoid infinite recursion when
        implementing custom attribute access methods.
    """
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

    def __init__(
        self,
        head: dict | None = None,
        label: str | None = None,
        _filename: str | Path | None = None,
    ):
        head = head or {}
        super().__init__(head)
        self.__dict__["_memoized"] = {}
        self.__dict__["_label"] = label
        self.__dict__["_filename"] = Path(_filename) if _filename is not None else None

        # TODO:
        #    if _filename was not given as an argument, we might want to check if the `head` has a `_filename` and do
        #    something like:
        #
        #    if _filename is None and isinstance(head, navdict):
        #        _filename = head.__dict__["_filename"]
        #        self.__dict__["_filename"] = _filename

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
                setattr(self, key, super().__getitem__(key))

    def get_label(self) -> str | None:
        return self.__dict__["_label"]

    def set_label(self, value: str):
        self.__dict__["_label"] = value

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

    @staticmethod
    def _alias_hook(key: str) -> str:
        raise NotImplementedError

    def set_alias_hook(self, hook: Callable[[str], str]):
        """
        Sets an alias (hook) function that maps the given argument, an attribute
        or a dict key, to a valid attribute or key.

        The `hook` function accepts a string argument and return a string for
        which the argument is an alias. The returned argument is expected to
        be a valid attribute or key for this navdict.
        """
        setattr(self, "_alias_hook", hook)

    # This method is called:
    #   - for *every* single attribute access on an object using dot notation.
    #   - when using the `getattr(obj, 'name') function
    #   - accessing any kind of attributes, e.g. instance or class variables,
    #     methods, properties, dunder methods, ...
    #
    # Note: `__getattr__` is only called when an attribute cannot be found
    #       through normal means.
    def __getattribute__(self, key):
        # logger.info(f"called __getattribute__({key}) ...")
        try:
            value = object.__getattribute__(self, key)
        except AttributeError:
            try:
                alias = self._alias_hook(key)
                value = object.__getattribute__(self, alias)
            except NotImplementedError:
                raise AttributeError(f"{type(self).__name__!r} object has no attribute {key!r}")

        if key.startswith("__"):  # small optimization
            return value
        # We can not directly call the `_handle_directive` function here due to infinite recursion
        if is_directive(value):
            m = object.__getattribute__(self, "_handle_directive")
            return m(key, value)
        else:
            return value

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
        try:
            value = super().__getitem__(key)
        except KeyError:
            try:
                alias = self._alias_hook(key)
                value = super().__getitem__(alias)
            except NotImplementedError:
                raise KeyError(f"{type(self).__name__!r} has no key {key!r}")

        if isinstance(key, str) and key.startswith("__"):
            return value
        # no danger for recursion here, so we can directly call the function
        if is_directive(value):
            return self._handle_directive(key, value)
        else:
            return value

    def _handle_directive(self, key, value) -> Any:
        """
        This method will handle the available directives. This may be builtin directives
        like `class/` or `factory//`, or it may be external directives that were provided
        as a plugin. Some builtin directives have also been provided as a plugin, e.g.
        'yaml//' and 'csv//'.

        Args:
            key: the key of the field that might contain a directive
            value: the value which might be a directive

        Returns:
            This function will return the value, either the original value or the result of
                evaluating and executing a directive.
        """
        # logger.debug(f"called _handle_directive({key}, {value!r}) [id={id(self)}]")

        directive_key, directive_value = unravel_directive(value)
        # logger.debug(f"{directive_key=}, {directive_value=}")

        if directive := get_directive_plugin(directive_key):
            # logger.debug(f"{directive.name=}")

            if key in self.__dict__["_memoized"]:
                return self.__dict__["_memoized"][key]

            args, kwargs = self._get_args_and_kwargs(key)
            parent_location = self._get_location()
            result = directive.func(directive_value, parent_location, *args, **kwargs)

            self.__dict__["_memoized"][key] = result
            return result

        match directive_key:
            case "class":
                args, kwargs = self._get_args_and_kwargs(key)
                return load_class(directive_value)(*args, **kwargs)

            case "factory":
                factory_args = _get_attribute(self, f"{key}_args", {})
                return load_class(directive_value)().create(**factory_args)

            case "int_enum":
                content = object.__getattribute__(self, "content")
                return load_int_enum(directive_value, content)

            case _:
                return value

    def _get_location(self):
        """Returns the location of the file from which this NavDict was loaded or None if no location exists."""
        try:
            filename = self.__dict__["_filename"]
            return filename.parent if filename else None
        except KeyError:
            return None

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

    def has_private_attribute(self, key) -> bool:
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

    def del_memoized_key(self, key: str):
        try:
            del self.__dict__["_memoized"][key]
            return True
        except KeyError:
            return False

    @staticmethod
    def from_dict(my_dict: dict, label: str | None = None) -> NavigableDict:
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
    def from_yaml_string(yaml_content: str | None = None, label: str | None = None) -> NavigableDict:
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

        yaml = YAML(typ="safe")
        try:
            data = yaml.load(yaml_content)
        except ScannerError as exc:
            raise ValueError(f"Invalid YAML string: {exc}")

        return NavigableDict(data, label=label)

    @staticmethod
    def from_yaml_file(filename: str | Path | None = None) -> NavigableDict:
        """Creates a navigable dictionary from the given YAML file.

        Args:
            filename (str): the path of the YAML file to be loaded

        Returns:
            a navdict that was loaded from the given location.

        Raises:
            ValueError: when no filename is given.
        """

        # logger.debug(f"{filename=}")

        if not filename:
            raise ValueError("Invalid argument to function: No filename or None given.")

        # Make sure the filename exists and is a regular file
        filename = Path(filename).expanduser().resolve()
        if not filename.is_file():
            raise ValueError(f"Invalid argument to function, filename does not exist: {filename!s}")

        data = load_yaml(str(filename))

        if data == {}:
            warnings.warn(f"Empty YAML file: {filename!s}")

        return data

    def to_yaml_file(self, filename: str | Path | None = None, header: str = None, top_level_group: str = None) -> None:
        """Saves a NavigableDict to a YAML file.

        When no filename is provided, this method will look for a 'private' attribute
        `_filename` and use that to save the data.

        Args:
            filename (str|Path): the path of the YAML file where to save the data
            header (str): Custom header for this navdict
            top_level_group (str): name of the optional top-level group

        Note:
            This method will **overwrite** the original or given YAML file and therefore you might
            lose proper formatting and/or comments.

        """
        if filename is None and self.get_private_attribute("_filename") is None:
            raise ValueError("No filename given or known, can not save navdict.")

        if header is None:
            header = textwrap.dedent(
                f"""
                # This YAML file is generated by:
                #
                #    navdict.to_yaml_file(setup, filename="{filename}')
                #
                # Created on {datetime.datetime.now(tz=datetime.timezone.utc).isoformat()}

                """
            )

        with Path(filename).open("w") as fd:
            fd.write(header)
            indent = 0
            if top_level_group:
                fd.write(f"{top_level_group}:\n")
                indent = 1

            self._save(fd, indent=indent)

        self.set_private_attribute("_filename", Path(filename))

    def get_filename(self) -> str | None:
        """Returns the filename for this navdict or None when no filename could be determined."""
        return self.get_private_attribute("_filename")


navdict = NavigableDict
NavDict = NavigableDict
"""Shortcuts for NavigableDict and more Pythonic."""


def _walk_dict_tree(dictionary: dict, tree: Tree, text_style: str = "green"):
    for k, v in dictionary.items():
        if isinstance(v, dict):
            branch = tree.add(f"[purple]{k}", style="", guide_style="dim")
            _walk_dict_tree(v, branch, text_style=text_style)
        else:
            text = Text.assemble((str(k), "medium_purple1"), ": ", (str(v), text_style))
            tree.add(text)
