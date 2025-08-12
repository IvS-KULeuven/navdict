__all__ = [
    "Directive",
    "get_directive_plugin",
    "is_directive",
    "load_directive_plugins",
    "unravel_directive",
    "register_directive",
]

import logging
import re
from importlib.metadata import EntryPoint
from importlib.metadata import entry_points
from typing import Callable
from typing import overload

DIRECTIVE_PATTERN = re.compile(r"^([a-zA-Z]\w+)/{2}(.*)$")

logger = logging.getLogger("navdict")


class Directive:
    @overload
    def __init__(self, ep: EntryPoint): ...

    @overload
    def __init__(self, *, name: str, func: Callable): ...

    def __init__(self, ep: EntryPoint | None = None, *, name: str | None = None, func: Callable | None = None):
        self.ep: EntryPoint | None = None
        self.directive_name: str | None = None
        self.directive_func: Callable | None = None

        if ep is not None:
            self.ep = ep
        elif name is not None and func is not None:
            self.directive_name = name
            self.directive_func = func
        else:
            raise ValueError("Must provide either 'ep' or both 'name' and 'func'")

    @property
    def name(self) -> str:
        return self.ep.name if self.ep else self.directive_name

    @property
    def func(self) -> Callable:
        return self.ep.load() if self.ep else self.directive_func


# Keep a record of all navdict directive plugins
_directive_plugins: dict[str, Directive] = {}


def register_directive(name: str, func: Callable):
    _directive_plugins[name] = Directive(name=name, func=func)


def load_directive_plugins():
    """
    Load any navdict directive plugins that are available in your environment.
    """
    global _directive_plugins

    eps = entry_points()
    # logger.debug(f"entrypoint groups: {sorted(eps.groups)}")
    eps = eps.select(group="navdict.directive")

    for ep in eps:
        _directive_plugins[ep.name] = Directive(ep=ep)


def is_directive(value: str) -> bool:
    """Returns True if the value matches a directive pattern, i.e. 'name//value'."""
    if isinstance(value, str):
        match = re.match(DIRECTIVE_PATTERN, value)
        return match is not None
    else:
        return False


def unravel_directive(value: str) -> tuple[str, str]:
    """
    Returns the directive key and the directive value in a tuple.

    Raises:
        A ValueError if the given value is not a directive.
    """
    match = re.match(DIRECTIVE_PATTERN, value)
    if match:
        return match[1], match[2]
    else:
        raise ValueError(f"Value is not a directive: {value}")


def get_directive_plugin(name: str) -> Directive | None:
    """Returns the directive that matches the given name or None if no plugin was loaded with that name."""
    return _directive_plugins.get(name)


# Load all directive plugins during import
load_directive_plugins()
