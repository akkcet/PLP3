
import pytest

from generated_components.submit_button import (
    submit_button
)


def test_submit_button_returns_value():

    result = submit_button()

    assert result is not None


def test_submit_button_returns_expected_type():

    result = submit_button()

    assert isinstance(
        result,
        (dict, list, bool, str, int, float)
    )
