import sys

import pytest


def main():
    sys.exit(
        pytest.main(["-v", "--cov=src", "--cov-branch", "--cov-report=xml"])
    )


if __name__ == "__main__":
    main()
