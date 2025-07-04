from dataclasses import dataclass
from importlib.metadata import EntryPoint
from typing import Callable


@dataclass
class Directive:
    ep: EntryPoint

    @property
    def name(self) -> str: ...
    @property
    def func(self) -> Callable: ...

def is_directive(value: str) -> bool: ...
def get_directive_plugin(name: str) -> Directive | None: ...
def unravel_directive(value: str) -> tuple[str, str]: ...
