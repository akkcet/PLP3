
import pytest

from generated_components.input_form import (
    input_form
)


def test_input_form_returns_value():

    result = input_form()

    assert result is not None


def test_input_form_returns_expected_type():

    result = input_form()

    assert isinstance(
        result,
        (dict, list, bool, str, int, float)
    )
