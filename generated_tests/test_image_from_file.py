
import pytest

from generated_components.image_from_file import (
    image_from_file
)


def test_image_from_file_returns_value():

    result = image_from_file()

    assert result is not None


def test_image_from_file_returns_expected_type():

    result = image_from_file()

    assert isinstance(
        result,
        (dict, list, bool, str, int, float)
    )
