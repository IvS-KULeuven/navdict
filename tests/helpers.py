from __future__ import annotations

import os
import textwrap
from pathlib import Path


def create_empty_file(filename: str | Path, create_folder: bool = False):
    """
    A function and context manager to create an empty file with the given
    filename. When used as a function, the file needs to be removed explicitly
    with a call to `filename.unlink()` or `os.unlink(filename)`.

    This function can be called as a context manager in which case the file will
    be removed when the context ends.

    Returns:
        The filename as a Path.
    """

    class _ContextManager:
        def __init__(self, filename: str | Path, create_folder: bool):
            self.filename = Path(filename)

            if self.filename.exists():
                raise FileExistsError(f"The empty file you wanted to create already exists: {filename}")

            if create_folder and not self.filename.parent.exists():
                self.filename.parent.mkdir(parents=True)

            with self.filename.open(mode="w"):
                pass

        def __enter__(self):
            return self.filename

        def __exit__(self, exc_type, exc_val, exc_tb):
            self.filename.unlink()

    return _ContextManager(filename, create_folder)


def create_text_file(filename: str | Path, content: str, create_folder: bool = False):
    """
    A function and context manager to create a text file with the given string
    as content. When used as a function, the file needs to be removed explicitly
    with a call to `filename.unlink()` or `os.unlink(filename)`.

    This function can be called as a context manager in which case the file will
    be removed when the context ends.

    >> with create_text_file("samples.txt", "A,B,C\n1,2,3\n4,5,6\n"):
    ..     # do something with the file or its content

    Returns:
        The filename as a Path.
    """

    class _ContextManager:
        def __init__(self, filename: str | Path, create_folder: bool):
            self.filename = Path(filename)

            if self.filename.exists():
                raise FileExistsError(f"The text file you wanted to create already exists: {filename}")

            if create_folder and not self.filename.parent.exists():
                self.filename.parent.mkdir(parents=True)

            with self.filename.open(mode="w") as fd:
                fd.write(content)

        def __enter__(self):
            return self.filename

        def __exit__(self, exc_type, exc_val, exc_tb):
            self.filename.unlink()

    return _ContextManager(filename, create_folder)

# Test the helper functions


def main():
    print(f"cwd = {os.getcwd()}")

    fn = Path("xxx.txt")

    with create_empty_file(fn):
        assert fn.exists()
    assert not fn.exists()

    create_empty_file(fn)
    assert fn.exists()
    fn.unlink()
    assert not fn.exists()

    # Test the create_a_text_file() helper function

    with create_text_file(
        fn,
        textwrap.dedent(
            """\
        A,B,C,D
        1,2,3,4
        5,6,7,8
        """
        ),
    ) as filename:
        assert fn.exists()
        assert filename == fn

        print(fn.read_text())

    assert not fn.exists()

    fn = Path("data/xxx.txt")

    with create_empty_file(fn, create_folder=True):
        assert fn.exists()

    assert not fn.exists()


if __name__ == "__main__":
    main()
