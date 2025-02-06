import sys

import pytest


def main():
    """
    Runs the pytest framework with coverage options.

    This function executes pytest with the following options:
    - `-v`: verbose mode
    - `--cov=src`: measure code coverage for the `src` directory
    - `--cov-branch`: measure branch coverage
    - `--cov-report=xml`: generate a coverage report in XML format

    The function exits with the status code returned by pytest.

    Returns:
        None
    """
    sys.exit(
        pytest.main(["-v", "--cov=src", "--cov-branch", "--cov-report=xml"])
    )


if __name__ == "__main__":
    main()
