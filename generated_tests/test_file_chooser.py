
import pytest

from generated_components.file_chooser import (
    file_chooser
)


def test_file_chooser_returns_value():

    result = file_chooser()

    assert result is not None


def test_file_chooser_returns_expected_type():

    result = file_chooser()

    assert isinstance(
        result,
        (dict, list, bool, str, int, float)
    )
