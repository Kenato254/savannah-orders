import pytest
import sys


def main():
    sys.exit(
        pytest.main(
            ["-v", "-s", "--cov=src", "--cov-branch", "--cov-report=xml"]
        )
    )


if __name__ == "__main__":
    main()
