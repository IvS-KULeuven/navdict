import enum
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

YAML_STRING_WITH_INT_ENUM = """
F_FEE:
    ccd_sides:
        enum: int_enum//FEE_SIDES
        content:
            E:
                alias: ['E_SIDE', 'RIGHT_SIDE']
                value: 1
            F:
                alias: ['F_SIDE', 'LEFT_SIDE']
                value: 0
"""

YAML_STRING_WITH_UNKNOWN_CLASS = """
root:
    part_one:
        cls: class//navdict.navdict
    part_two:
        cls: class//unknown.navdict
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

    with create_text_file("with_unknown_class.yaml", YAML_STRING_WITH_UNKNOWN_CLASS) as fn:
        # The following line shall not generate an exception, meaning the `class//`
        # shall not be evaluated on load!
        data = navdict.from_yaml_file(fn)

        assert "root" in data
        assert isinstance(data.root.part_one.cls, navdict)

        # Only when accessed, it will generate an exception.
        with pytest.raises(ModuleNotFoundError, match="No module named 'unknown'"):
            _ = data.root.part_two.cls


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


def get_enum_metaclass():
    """Get the enum metaclass in a version-compatible way."""
    if hasattr(enum, 'EnumMeta'):
        return enum.EnumMeta
    elif hasattr(enum, 'EnumType'):  # Python 3.11+
        return enum.EnumType
    else:
        # Fallback: get it from a known enum
        return type(enum.IntEnum)


def test_int_enum():

    setup = navdict.from_yaml_string(YAML_STRING_WITH_INT_ENUM)

    assert "enum" in setup.F_FEE.ccd_sides
    assert "content" in setup.F_FEE.ccd_sides
    assert "E" in setup.F_FEE.ccd_sides.content
    assert "F" in setup.F_FEE.ccd_sides.content

    assert setup.F_FEE.ccd_sides.enum.E.value == 1
    assert setup.F_FEE.ccd_sides.enum.E_SIDE.value == 1
    assert setup.F_FEE.ccd_sides.enum.RIGHT_SIDE.value == 1
    assert setup.F_FEE.ccd_sides.enum.RIGHT_SIDE.name == 'E'

    assert setup.F_FEE.ccd_sides.enum.F.value == 0
    assert setup.F_FEE.ccd_sides.enum.F_SIDE.value == 0
    assert setup.F_FEE.ccd_sides.enum.LEFT_SIDE.value == 0
    assert setup.F_FEE.ccd_sides.enum.LEFT_SIDE.name == 'F'

    assert issubclass(setup.F_FEE.ccd_sides.enum, enum.IntEnum)
    assert isinstance(setup.F_FEE.ccd_sides.enum, get_enum_metaclass())
    assert isinstance(setup.F_FEE.ccd_sides.enum, type)
    assert isinstance(setup.F_FEE.ccd_sides.enum.E, enum.IntEnum)  # noqa


YAML_STRING_LOADS_YAML_FILE = """
root:
    simple: yaml//enum.yaml
"""


def test_recursive_load():

    with (
        create_text_file("load_yaml.yaml", YAML_STRING_LOADS_YAML_FILE) as fn,
        create_text_file("enum.yaml", YAML_STRING_WITH_INT_ENUM)
    ):
        data = navdict.from_yaml_file(fn)
        assert data.root.simple.F_FEE.ccd_sides.enum.E.value == 1
