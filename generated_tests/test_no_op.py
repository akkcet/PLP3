
import pytest

from generated_components.no_op import (
    no_op
)


def test_no_op_returns_value():

    result = no_op()

    assert result is not None


def test_no_op_returns_expected_type():

    result = no_op()

    assert isinstance(
        result,
        (dict, list, bool, str, int, float)
    )
