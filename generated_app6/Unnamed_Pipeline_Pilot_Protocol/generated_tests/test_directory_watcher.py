
import pytest

from generated_components.directory_watcher import (
    directory_watcher
)


def test_directory_watcher_returns_value():

    result = directory_watcher()

    assert result is not None


def test_directory_watcher_returns_expected_type():

    result = directory_watcher()

    assert isinstance(
        result,
        (dict, list, bool, str, int, float)
    )
