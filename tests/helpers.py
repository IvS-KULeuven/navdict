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


CSV_TEST_DATA = """\
employee_id,first_name,last_name,department,position,salary,hire_date,is_active,email
# a comment line
1001,John,Smith,Engineering,Software Engineer,75000,2022-03-15,TRUE,john.smith@company.com
1002,Sarah,Johnson,Marketing,Marketing Manager,68000,2021-07-22,TRUE,sarah.johnson@company.com
1003,Michael,Brown,Sales,Sales Representative,55000,2023-01-10,TRUE,michael.brown@company.com
1004,Emily,Davis,Engineering,Senior Developer,85000,2020-11-05,TRUE,emily.davis@company.com
1005,David,Wilson,HR,HR Specialist,62000,2022-09-18,TRUE,david.wilson@company.com
1006,Lisa,Anderson,Finance,Financial Analyst,70000,2021-04-12,TRUE,lisa.anderson@company.com
1007,Robert,Taylor,Engineering,DevOps Engineer,78000,2022-12-03,TRUE,robert.taylor@company.com
1008,Jennifer,Thomas,Marketing,Content Creator,52000,2023-05-20,TRUE,jennifer.thomas@company.com
1009,William,Jackson,Sales,Sales Manager,72000,2020-08-14,TRUE,william.jackson@company.com
1010,Jessica,White,IT,System Administrator,65000,2021-10-30,FALSE,jessica.white@company.com
1011,Christopher,Harris,Engineering,Junior Developer,58000,2023-08-07,TRUE,christopher.harris@company.com
1012,Amanda,Martin,Finance,Accountant,61000,2022-02-28,TRUE,amanda.martin@company.com
1013,James,Thompson,Sales,Sales Representative,54000,2023-03-16,TRUE,james.thompson@company.com
1014,Michelle,Garcia,HR,Recruiter,59000,2021-12-08,TRUE,michelle.garcia@company.com
1015,Daniel,Rodriguez,IT,Network Engineer,73000,2020-06-25,TRUE,daniel.rodriguez@company.com
"""


def create_test_csv_file(filename: str | Path, create_folder: bool = False):
    """
    This file includes 15 employees with various data types that are useful for testing:

    - Employee IDs (integers)
    - Names (text strings)
    - Departments (Engineering, Marketing, Sales, HR, Finance, IT)
    - Salaries (numeric values)
    - Hire dates (date format)
    - Active status (boolean TRUE/FALSE)
    - Email addresses (text with special characters)

    The data includes different scenarios like active/inactive employees, various salary ranges,
    and different departments, making it great for testing data filtering, sorting, analysis,
    and visualization.

    """
    return create_text_file(filename, CSV_TEST_DATA, create_folder)


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
