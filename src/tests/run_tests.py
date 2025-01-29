import pytest
import sys


def main():
    sys.exit(pytest.main(["-v", "-s"]))


if __name__ == "__main__":
    main()
