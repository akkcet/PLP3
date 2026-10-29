
import pytest

from generated_components.dynamic_content_container import (
    dynamic_content_container
)


def test_dynamic_content_container_returns_value():

    result = dynamic_content_container()

    assert result is not None


def test_dynamic_content_container_returns_expected_type():

    result = dynamic_content_container()

    assert isinstance(
        result,
        (dict, list, bool, str, int, float)
    )
