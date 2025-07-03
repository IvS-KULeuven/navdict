from pathlib import Path
from typing import TypeAlias

class NavigableDict(dict):
    def __init__(
        self,
        head: dict | None = ...,
        label: str | None = ...,
        _filename: str | Path | None = ...,
    ): ...
    @staticmethod
    def from_yaml_file(filename: str | Path | None = ...) -> NavigableDict: ...

navdict: TypeAlias = NavigableDict
NavDict: TypeAlias = NavigableDict
