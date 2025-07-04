from pathlib import Path
from typing import TypeAlias

def load_yaml(resource_name: str, parent: NavigableDict | None = ...) -> NavDict: ...
def load_csv(resource_name: str, *args, parent: navdict | None = None, **kwargs): ...
def get_resource_location(parent_location: Path | None, in_dir: str | None) -> Path: ...


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
