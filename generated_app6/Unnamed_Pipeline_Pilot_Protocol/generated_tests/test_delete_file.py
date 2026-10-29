
import pytest

from generated_components.delete_file import (
    delete_file
)


def test_delete_file_returns_value():

    result = delete_file()

    assert result is not None


def test_delete_file_returns_expected_type():

    result = delete_file()

    assert isinstance(
        result,
        (dict, list, bool, str, int, float)
    )
