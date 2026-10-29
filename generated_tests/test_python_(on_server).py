
import pytest

from generated_components.python_(on_server) import (
    python_(on_server)
)


def test_python_(on_server)_returns_value():

    result = python_(on_server)()

    assert result is not None


def test_python_(on_server)_returns_expected_type():

    result = python_(on_server)()

    assert isinstance(
        result,
        (dict, list, bool, str, int, float)
    )
