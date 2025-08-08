"""
Default directive plugins that are used in NavigableDict.

This module also serves as a guideline how to implement the directive plugins. The plugins are called with the
following interface:

    plugin_func(value: str, parent_location: Path | None, *args, **kwargs)

where:

    - value: this is the directive value, i.e. the part that comes after the double slash '//'.
    - parent_location: this is the location of the navdict where this directive was found and
          this can be used to determine the location of a resource.
    - args: any positional arguments that were given in the YAML file under '<key>_args'.
    - kwargs: any keyword arguments that were given in the YAML file under '<key>_kwargs'.

"""

import logging
import os
from pathlib import Path

from navdict.navdict import load_yaml as _load_yaml
from navdict.navdict import load_csv as _load_csv

logger = logging.getLogger("navdict.plugin")


def load_yaml(value: str, parent_location: Path | None, *args, **kwargs):
    # logger.debug(f"Loading YAML file: '{value}'.")

    return _load_yaml(value, parent_location)


def load_csv(value: str, parent_location: Path | None, *args, **kwargs):
    # logger.debug(f"Loading CSV file: '{value}'.")

    return _load_csv(value, parent_location, *args, **kwargs)


def env_var(value: str, parent_location: Path | None, *args, **kwargs):
    # logger.debug(f"Loading environment variable: '{value}'.")

    return os.environ.get(value)


# TODO:
#   I can have 'panda' as an optional dependency and provide a pandas directive here.
