
import pytest

from generated_components.tile_vertical import (
    tile_vertical
)


def test_tile_vertical_returns_value():

    result = tile_vertical()

    assert result is not None


def test_tile_vertical_returns_expected_type():

    result = tile_vertical()

    assert isinstance(
        result,
        (dict, list, bool, str, int, float)
    )
