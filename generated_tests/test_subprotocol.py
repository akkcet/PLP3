
import pytest

from generated_components.subprotocol import (
    subprotocol
)


def test_subprotocol_returns_value():

    result = subprotocol()

    assert result is not None


def test_subprotocol_returns_expected_type():

    result = subprotocol()

    assert isinstance(
        result,
        (dict, list, bool, str, int, float)
    )
