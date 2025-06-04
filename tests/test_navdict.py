from pathlib import Path

import pytest

from navdict import navdict
from tests.helpers import create_text_file


class TakeTwoOptionalArguments:
    """Test class for YAML load and save methods."""

    def __init__(self, a=23, b=24):
        super().__init__()
        self._a = a
        self._b = b

    def __str__(self):
        return f"a={self._a}, b={self._b}"


YAML_STRING_SIMPLE = """
Setup:
    site_id: KUL
    
    gse:
        hexapod:
            id:    PUNA_01

"""

YAML_STRING_WITH_CLASS = """
root:
    defaults:
        dev: class//test_navdict.TakeTwoOptionalArguments
    with_args:
        dev: class//test_navdict.TakeTwoOptionalArguments
        dev_args: [42, 73]
"""

YAML_STRING_INVALID_INDENTATION = """
name: test
  age: 30
description: invalid indentation
"""

YAML_STRING_MISSING_COLON = """
name test
age: 30
"""

YAML_STRING_EMPTY = """"""


def test_construction():

    setup = navdict()

    assert setup == {}
    assert setup.label is None

    setup = navdict(label="Setup")
    assert setup.label == "Setup"


def test_from_yaml_string():

    setup = navdict.from_yaml_string(YAML_STRING_SIMPLE)

    assert "Setup" in setup
    assert "site_id" in setup.Setup
    assert "gse" in setup.Setup
    assert setup.Setup.gse.hexapod.id == "PUNA_01"

    with pytest.raises(ValueError, match="Invalid YAML string: mapping values are not allowed in this context"):
        setup = navdict.from_yaml_string(YAML_STRING_INVALID_INDENTATION)

    with pytest.raises(ValueError, match="Invalid YAML string: mapping values are not allowed in this context"):
        setup = navdict.from_yaml_string(YAML_STRING_MISSING_COLON)

    with pytest.raises(ValueError, match="Invalid argument to function: No input string or None given"):
        setup = navdict.from_yaml_string(YAML_STRING_EMPTY)


def test_from_yaml_file():

    with create_text_file("simple.yaml", YAML_STRING_SIMPLE) as fn:
        setup = navdict.from_yaml_file(fn)
        assert "Setup" in setup
        assert "site_id" in setup.Setup
        assert "gse" in setup.Setup
        assert setup.Setup.gse.hexapod.id == "PUNA_01"


def test_to_yaml_file():
    """
    This test loads the standard Setup and saves it without change to a new file.
    Loading back the saved Setup should show no differences.
    """

    setup = navdict.from_yaml_string(YAML_STRING_SIMPLE)
    setup.to_yaml_file("simple.yaml")

    setup = navdict.from_yaml_string(YAML_STRING_WITH_CLASS)
    setup.to_yaml_file("with_class.yaml")

    Path("simple.yaml").unlink()
    Path("with_class.yaml").unlink()


def test_class_directive():

    setup = navdict.from_yaml_string(YAML_STRING_WITH_CLASS)

    obj = setup.root.defaults.dev
    assert isinstance(obj, TakeTwoOptionalArguments)
    assert str(obj) == "a=23, b=24"

    obj = setup.root.with_args.dev
    assert isinstance(obj, TakeTwoOptionalArguments)
    assert str(obj) == "a=42, b=73"


def test_from_dict():

    setup = navdict.from_dict({"ID": "my-setup-001", "version": "0.1.0"}, label="Setup")
    assert setup["ID"] == setup.ID == "my-setup-001"

    assert setup._label == "Setup"

    # If not all keys are of type 'str', the navdict will not be navigable.
    setup = navdict.from_dict({"ID": 1234, 42: "forty two"}, label="Setup")
    assert setup["ID"] == 1234

    with pytest.raises(AttributeError):
        _ = setup.ID

    # Only the (sub-)dictionary that contains non-str keys will not be navigable.
    setup = navdict.from_dict({"ID": 1234, "answer": {"book": "H2G2", 42: "forty two"}}, label="Setup")
    assert setup["ID"] == setup.ID == 1234
    assert setup.answer["book"] == "H2G2"

    with pytest.raises(AttributeError):
        _ = setup.answer.book
