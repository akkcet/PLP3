
import pytest

from generated_components.text import (
    text
)


def test_text_returns_value():

    result = text()

    assert result is not None


def test_text_returns_expected_type():

    result = text()

    assert isinstance(
        result,
        (dict, list, bool, str, int, float)
    )
