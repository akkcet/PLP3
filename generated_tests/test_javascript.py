
import pytest

from generated_components.javascript import (
    javascript
)


def test_javascript_returns_value():

    result = javascript()

    assert result is not None


def test_javascript_returns_expected_type():

    result = javascript()

    assert isinstance(
        result,
        (dict, list, bool, str, int, float)
    )
