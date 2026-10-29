
import pytest

from generated_components.include import (
    include
)


def test_include_returns_value():

    result = include()

    assert result is not None


def test_include_returns_expected_type():

    result = include()

    assert isinstance(
        result,
        (dict, list, bool, str, int, float)
    )
