import enum
import os
from pathlib import Path

import pytest

from helpers import create_test_csv_file
from helpers import create_text_file
from navdict import navdict
from navdict.directive import Directive
from navdict.directive import get_directive_plugin
from navdict.directive import is_directive
from navdict.directive import register_directive
from navdict.navdict import get_resource_location

HERE = Path(__file__).parent


class TakeTwoOptionalArguments:
    """Test class for YAML load and save methods."""

    def __init__(self, a=23, b=24):
        super().__init__()
        self._a = a
        self._b = b

    def __str__(self):
        return f"a={self._a}, b={self._b}"


class TakeOneKeywordArgument:
    def __init__(self, *, sim: bool):
        self._sim = sim

    def __str__(self):
        return f"sim = {self._sim}"


YAML_STRING_SIMPLE = """
Setup:
    site_id: KUL
    
    gse:
        hexapod:
            id:    PUNA_01

"""

YAML_STRING_WITH_RELATIVE_YAML = """
Setup:
    camera:
        fm01: yaml//cameras/fm01.yaml
"""

YAML_STRING_WITH_CLASS = """
root:
    defaults:
        dev: class//test_navdict.TakeTwoOptionalArguments
    with_args:
        dev: class//test_navdict.TakeTwoOptionalArguments
        dev_args: [42, 73]
    with_kwarg:
        dev: class//test_navdict.TakeOneKeywordArgument
        dev_kwargs:
            sim: true
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


def test_is_directive():
    assert is_directive("yaml//sample.yaml")
    assert is_directive("class//navdict.navdict")
    assert is_directive("my_directive//value")

    assert not is_directive("just a string")
    assert not is_directive("relative/path")
    assert not is_directive("my-directive//value")

    assert not is_directive(42)
    assert not is_directive(23.7)

    assert not is_directive("my-setup-001")


def test_get_directive_plugin():
    assert isinstance(get_directive_plugin("yaml"), Directive)

    assert not isinstance(get_directive_plugin("not-a-plugin"), Directive)


def test_use_a_directive_plugin():
    yaml_string = """
    Setup:
        info: my_yaml//../use/this/file.yaml
        info_args: [1, 2]
        info_kwargs:
            x: X
            y: Y
    """
    data = navdict.from_yaml_string(yaml_string)
    # print(f"{data.Setup.info=}")
    assert data.Setup.info.startswith("my_yaml//")
    assert data.Setup.info.endswith("use/this/file.yaml")


def test_get_resource_location():
    assert get_resource_location(None, None) == Path(".")
    assert get_resource_location(None, "../data") == Path(".") / "../data"
    assert get_resource_location(Path("~"), "data") == Path("~") / "data"
    assert get_resource_location(Path("~"), None) == Path("~")


def test_construction():
    setup = navdict()

    assert setup == {}
    assert setup.get_label() is None

    setup = navdict(label="Setup")
    assert setup.get_label() == "Setup"


def test_label():
    setup = navdict()

    assert setup == {}
    assert setup.get_label() is None

    setup.set_label("Setup")

    assert setup == {}
    assert setup.get_label() == "Setup"


def test_navigation():
    data = navdict.from_yaml_string(YAML_STRING_SIMPLE)

    assert isinstance(data, navdict)
    assert isinstance(data.Setup, navdict)

    assert data.Setup.site_id == "KUL"
    assert data.Setup.gse.hexapod.id == "PUNA_01"


def test_from_yaml_string():
    setup = navdict.from_yaml_string(YAML_STRING_SIMPLE)

    assert "Setup" in setup
    assert "site_id" in setup.Setup
    assert "gse" in setup.Setup
    assert setup.Setup.gse.hexapod.id == "PUNA_01"

    with pytest.raises(
        ValueError,
        match="Invalid YAML string: mapping values are not allowed in this context",
    ):
        setup = navdict.from_yaml_string(YAML_STRING_INVALID_INDENTATION)

    with pytest.raises(
        ValueError,
        match="Invalid YAML string: mapping values are not allowed in this context",
    ):
        setup = navdict.from_yaml_string(YAML_STRING_MISSING_COLON)

    with pytest.raises(ValueError, match="Invalid argument to function: No input string or None given"):
        setup = navdict.from_yaml_string(YAML_STRING_EMPTY)


def test_from_yaml_file():
    with pytest.raises(
        ValueError,
        match=r"Invalid argument to function, filename does not exist: "
        r".*/simple.yaml",
    ):
        navdict.from_yaml_file("~/simple.yaml")

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

    with pytest.raises(ValueError, match="No filename given or known, can not save navdict."):
        setup.to_yaml_file()

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

    obj = setup.root.with_kwarg.dev
    assert isinstance(obj, TakeOneKeywordArgument)
    assert str(obj) == "sim = True"


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
    if hasattr(enum, "EnumMeta"):
        return enum.EnumMeta
    elif hasattr(enum, "EnumType"):  # Python 3.11+
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
    assert setup.F_FEE.ccd_sides.enum.RIGHT_SIDE.name == "E"

    assert setup.F_FEE.ccd_sides.enum.F.value == 0
    assert setup.F_FEE.ccd_sides.enum.F_SIDE.value == 0
    assert setup.F_FEE.ccd_sides.enum.LEFT_SIDE.value == 0
    assert setup.F_FEE.ccd_sides.enum.LEFT_SIDE.name == "F"

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
        create_text_file("enum.yaml", YAML_STRING_WITH_INT_ENUM),
    ):
        data = navdict.from_yaml_file(fn)
        assert data.root.simple.F_FEE.ccd_sides.enum.E.value == 1


def test_relative_load():
    with (
        create_text_file(HERE / "data/conf/load_relative_yaml.yaml", YAML_STRING_WITH_RELATIVE_YAML) as fn,
    ):
        data = navdict.from_yaml_file(fn)
        assert data.Setup.camera.fm01.calibration.temperature.T1.name == "TRP99"


def test_relative_load_from_string():
    """
    The YAML string contains a directive to load another YAML file, but since
    we will load this navdict from the string instead of the file, it doesn't
    have a location and therefore the directive will be loaded relative to the
    working directory.

    When we change the current working directory to the expected location, things
    work just fine.

    """
    data = navdict.from_yaml_string(YAML_STRING_WITH_RELATIVE_YAML)

    assert "fm01" in data.Setup.camera

    with pytest.raises(FileNotFoundError, match="No such file or directory: 'cameras/fm01.yaml'"):
        assert data.Setup.camera.fm01

    cwd = os.getcwd()

    os.chdir(HERE / "data/conf")

    assert data.Setup.camera.fm01.name == "FM01"
    assert "T1" in data.Setup.camera.fm01.calibration.temperature

    os.chdir(cwd)


YAML_STRING_LOADS_CSV_FILE = """
root:
    sample: csv//data/sample.csv
    sample_kwargs:
        header_rows: 1
"""


def test_load_csv():
    """
    The sample.csv file will be read using the standard load_csv directive.

    - one header row will be skipped (header_rows=1)
    - the comment line will be filtered
    - a list of list[str] will be returned

    """
    with (
        create_text_file(HERE / "load_csv.yaml", YAML_STRING_LOADS_CSV_FILE) as fn,
        create_test_csv_file(HERE / "data/sample.csv"),
    ):
        data = navdict.from_yaml_file(fn)

        csv_data = data.root.sample

        assert len(csv_data[0]) == 9
        assert isinstance(csv_data, list)
        assert isinstance(csv_data[0], list)

        assert csv_data[0][0] == "1001"
        assert csv_data[0][8] == "john.smith@company.com"


def test_directive_registration():
    def inspect_directive(value, parent_location, *args, **kwargs) -> dict:
        return dict(value=value, parent_location=parent_location, args=args, kwargs=kwargs)

    # The following should overwrite the default `csv//` directive
    register_directive("csv", inspect_directive)

    with (
        create_text_file(HERE / "load_csv.yaml", YAML_STRING_LOADS_CSV_FILE) as fn,
        create_test_csv_file(HERE / "data/sample.csv"),
    ):
        data = navdict.from_yaml_file(fn)

        csv_data = data.root.sample

        assert isinstance(csv_data, dict)
        assert "value" in csv_data
        assert csv_data["value"] == "data/sample.csv"
        assert csv_data["parent_location"] == HERE

        assert "kwargs" in csv_data
        assert "header_rows" in csv_data["kwargs"]
        assert csv_data["kwargs"]["header_rows"] == 1


YAML_STRING_WITH_ENV_VAR = """
config:
    token: env//AUTH_TOKEN
"""


def test_env_var():
    data = navdict.from_yaml_string(YAML_STRING_WITH_ENV_VAR)

    assert data.config.token is None

    os.environ["AUTH_TOKEN"] = "this-is-my-token"

    data.config.del_memoized_key("token")

    assert data.config.token == "this-is-my-token"

    del os.environ["AUTH_TOKEN"]


def test_memoized_keys():
    # NOTE:
    #   * memoized keys are only for directives.
    #   * a key is memoized only after it was accessed.

    data = navdict.from_yaml_string(YAML_STRING_WITH_ENV_VAR)

    assert data.config.get_memoized_keys() == []

    os.environ["AUTH_TOKEN"] = "this-is-my-token-too"

    assert data.config.token == "this-is-my-token-too"

    assert data.config.get_memoized_keys() == ["token"]

    assert data.config.del_memoized_key("token")

    assert "token" not in data.config.get_memoized_keys()

    # returns False when a key is not memoized and could not be deleted
    assert not data.config.del_memoized_key("unknown")


def test_non_string_keys():
    x = navdict({"A": {1: "one", 2: "two", (3,): "three-tuple"}})

    assert x.A[1] == "one"
    assert x.A[2] == "two"
    assert x.A[(3,)] == "three-tuple"


def test_invalid_yaml():
    # This would normally raise a ScannerError from the ruamel.yaml package
    #  -  ruamel.yaml.scanner.ScannerError: mapping values are not allowed in this context

    with pytest.raises(IOError):
        _ = navdict.from_yaml_file(__file__)


def test_alias_hook():
    x = navdict({"letters": {"a": "A", "b": "B", "c": "C"}, "numbers": [1, 2, 3, 4, 5]})

    def greek(letter: str):
        greek_to_latin = {"alpha": "a", "beta": "b", "gamma": "c"}
        return greek_to_latin[letter]

    assert x.letters.a == "A"
    assert x.numbers[2] == 3

    with pytest.raises(AttributeError):
        _ = x.letters.alpha

    with pytest.raises(KeyError):
        _ = x.letters["alpha"]

    x.letters.set_alias_hook(greek)

    assert x.letters.alpha == "A"
    assert x.letters["alpha"] == "A"

    assert x.numbers[2] == 3

def test_alias_hook_from_yaml_string():

    cams = """
    House:
        Cameras:
            cam_1:
                location: front door
                type: XYZ-A123
            cam_2:
                location: front garage
                type: XYZ-B123
    """

    iot = navdict.from_yaml_string(cams)

    assert iot.House.Cameras.cam_1.type == "XYZ-A123"
    assert iot.House.Cameras.cam_2.type == "XYZ-B123"

    def abbrev(name: str) -> str:
        aliases = {
            "front_door": "cam_1",
            "front_garage": "cam_2"
        }
        return aliases[name]

    iot.House.Cameras.set_alias_hook(abbrev)

    assert iot.House.Cameras.cam_1.type == "XYZ-A123"
    assert iot.House.Cameras.cam_2.type == "XYZ-B123"

    assert iot.House.Cameras.front_door.type == "XYZ-A123"
    assert iot.House.Cameras.front_garage.type == "XYZ-B123"
