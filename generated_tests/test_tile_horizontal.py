
import pytest

from generated_components.tile_horizontal import (
    tile_horizontal
)


def test_tile_horizontal_returns_value():

    result = tile_horizontal()

    assert result is not None


def test_tile_horizontal_returns_expected_type():

    result = tile_horizontal()

    assert isinstance(
        result,
        (dict, list, bool, str, int, float)
    )
