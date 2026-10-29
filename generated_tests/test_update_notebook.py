
import pytest

from generated_components.update_notebook import (
    update_notebook
)


def test_update_notebook_returns_value():

    result = update_notebook()

    assert result is not None


def test_update_notebook_returns_expected_type():

    result = update_notebook()

    assert isinstance(
        result,
        (dict, list, bool, str, int, float)
    )
