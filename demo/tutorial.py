import marimo

__generated_with = "0.17.0"
app = marimo.App(width="full")


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    # NavDict tutorial

    A `navdict` (short for `NavigableDict`) is an enhanced dictionary that goes beyond a standard Python dictionary by offering:

    - Navigation features to move through the data more easily
    - Automatic content loading capabilities
    - The ability to extend it with custom features

    This tutorial will guide you through the most important features.
    See the official documentation at [github.io](https://ivs-kuleuven.github.io/navdict/).
    """
    )
    return


@app.cell
def _():
    from navdict import navdict

    return (navdict,)


@app.cell
def _():
    house = """
    House:
        Cameras:
            cam_01:
                location: front door
                type: XYZ-F1234
            cam_02:
                location: front garage
                type: XYZ-F1234
            cam_03:
                location: back garage
                type: XYZ-B1234
            cam_04:
                location: backyard
                type: XYZ-B1234
    """

    return (house,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
    ## Creation

    A `navdict` can be created from a simple dictionary, from a YAML file or from a YAML string. All three posibilities are illustrated in the code snippet below.

    ```
    >>> x = navdict({'a': 1, 'b': 2})
    >>> settings = navdict.from_yaml_file(filename="~/data/settings.yaml")
    >>> iot = navdict.from_yaml_string(yaml_content=house, label="IoT")  # house is a string containing YAML
    ```

    Printing the last variable (`iot`) using the `rich` package results in the following output:
    """
    )
    return


@app.cell(hide_code=True)
def _(capture_stdout, house, mo, navdict, rich):
    iot = navdict.from_yaml_string(house, label="IoT")

    def _():
        rich.print(iot)

    mo.md(
        text=f"""
    ```
    >>> rich.print(iot)
    {capture_stdout(_)}
    ```
    """
    )
    return (iot,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ## Dot notation

    Unlike regular Python dictionaries that only support bracket notation (`dict['key']`), a `navdict` allows you to access values using dot notation (`navdict.key`) as well. This makes it feel more like working with object attributes and results in cleaner, more readable code.

    Dot notation is particularly valuable when working with nested data structures, as it eliminates the need for multiple sets of brackets and quotes. Instead of writing `dict['level1']['level2']['level3']`, you can simply write `navdict.level1.level2.level3`, which is much easier to read and less prone to syntax errors.

    This section demonstrates the dot-notation functionality. In the above navdict, if we want to see the content of cam_01, we can access it using either the traditional bracket notation or the more convenient dot notation:

    ```
    iot["House"]["Cameras"]["cam_01"]
    iot.House.Cameras.cam_01
    ```

    Both approaches return the same result, but the dot notation provides a more intuitive and streamlined syntax, especially when chaining multiple levels of access or when the key names are valid Python identifiers.
    """
    )
    return


@app.cell
def _(capture_stdout, iot, mo, rich):
    def _1():
        rich.print(iot.House.Cameras.cam_01)

    def _2():
        rich.print(iot["House"]["Cameras"]["cam_01"])

    mo.md(
        text=f"""
    When we print the above with the `rich` package, we get the following output:
    ```
    >>> rich.print(iot.House.Cameras.cam_01)
    {capture_stdout(_1)}

    >>> rich.print(iot["House"]["Cameras"]["cam_01"])
    {capture_stdout(_2)}
    ```
    """
    )
    return


@app.cell
def _(mo):
    mo.md(r"""## Making changes""")
    return


@app.cell
def _(iot):
    iot.House.Rooms = {
        "entrance": {"doors": 3, "windows": 1},
        "room_1": {"doors": 1, "windows": 2},
        "room_2": {"doors": 1, "windows": 1},
    }
    return


@app.cell
def _(mo):
    mo.md(
        r"""
    ### Adding new branches in the dictionary

    Let's add a definition for a few of the rooms in the house. In the branch _House_ we would add a key for the rooms and a value that is a dictionary describing the rooms.

    ```
    iot.House.Rooms = {
        "entrance": {"doors": 3, "windows": 1}, 
        "room_1": {"doors": 1, "windows": 2},
        "room_2": {"doors": 1, "windows": 1},
    }
    ```
    """
    )
    return


@app.cell
def _(capture_stdout, iot, mo, rich):
    def _():
        rich.print(iot.House)

    mo.md(
        text=f"""
    If we then print the _House_ branch, we see that the rooms have been added.
    ```
    >>> rich.print(iot.House)
    {capture_stdout(_)}
    ```
    """
    )

    return


@app.cell
def _(capture_stdout, iot, mo, rich):
    iot["House"]["Rooms"]["room_3"] = {"doors": 1, "windows": 3}
    iot.House.Rooms.room_4 = {"doors": 2, "windows": 3}

    def _():
        rich.print(iot.House.Rooms)

    mo.md(
        text=f"""
    You can also add a new key like you are used to with a normal dictionary. Both notations can be used, bracket- and dot-notation.
    ```
    iot["House"]["Rooms"]["room_3"] = {{'doors': 1, 'windows': 3}}
    iot.House.Rooms.room_4 = {{'doors': 2, 'windows': 3}}
    ```
    When we print the Rooms, we see that two rooms have been added.
    ```
    >>> rich.print(iot.House.Rooms)
    {capture_stdout(_)}
    ```
    """
    )

    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ## Aliases

    We can define aliases for all keys in a `navdict`. Aliases are alternative names for keys in your `navdict`. They allow you to access the same data using multiple different keys, which is useful when you want to support different naming conventions or provide shortcuts for longer key names.

    You can define aliases for any key in the navdict, allowing the same value to be accessed through multiple names. This is particularly useful for:

    - Supporting multiple naming conventions (e.g., `cam_01` and `front_door`)
    - Creating shortcuts for frequently used keys (e.g., `cfg` for `configuration`)
    - Maintaining backward compatibility when renaming keys

    Aliases are added to the `navdict` with the method `set_alias_hook()`. This method takes a function name as an argument. That function will be executed when the `navdict` is trying to resolve your key name.

    The alias hook function needs to take one string argument, which is the alias you specified as a key in the navigation. The function will then return a valid key or raise an exception. The key that is returned shall be a valid key for the navdict. In most cases, the alias hook function will be a mapping between aliases and a valid navdict key.

    The following code presents a simple example for our `Rooms` navdict:

    ```
    def alias_hook_rooms(alias: str) -> str:
        aliases = {
            "master_bedroom": "room_1",
            "kids_room": "room_2",
            "visitor_room": "room_3",
            "office": "room_4",
        }
        return aliases[alias]

    iot.House.Rooms.set_alias_hook(alias_hook_rooms)
    ```
    """
    )
    return


@app.cell
def _(iot):
    def alias_hook_rooms(alias: str) -> str:
        aliases = {
            "master_bedroom": "room_1",
            "kids_room": "room_2",
            "visitor_room": "room_3",
            "office": "room_4",
        }
        return aliases[alias]

    iot.House.Rooms.set_alias_hook(alias_hook_rooms)
    return


@app.cell
def _(capture_stdout, iot, mo, rich):
    def _1():
        rich.print(iot.House.Rooms.master_bedroom)  # this is room_1

    def _2():
        rich.print(iot.House.Rooms.visitor_room)  # this is room_3

    mo.md(
        text=f"""
    Now you can access the rooms using their aliases. Note however that in the print, the original valid key for the room is used.
    ```
    >>> rich.print(iot.House.Rooms.master_bedroom)
    {capture_stdout(_1)}
    >>> rich.print(iot.House.Rooms.visitor_room)
    {capture_stdout(_2)}
    ```
    """
    )
    return


@app.cell
def _(mo):
    mo.md(
        r"""
    ## TODO

    - Section on Directives
    - Section on plugins (for directives)
    """
    )
    return


@app.cell
def _():
    import marimo as mo
    import rich
    import sys
    import textwrap

    return mo, rich


@app.cell
def _():
    from contextlib import redirect_stdout
    import io

    def capture_stdout(func: callable) -> str:
        output = io.StringIO()
        with redirect_stdout(output):
            func()
        return output.getvalue()

    return (capture_stdout,)


if __name__ == "__main__":
    app.run()
