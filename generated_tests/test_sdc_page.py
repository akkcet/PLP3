
import pytest

from generated_components.sdc_page import (
    sdc_page
)


def test_sdc_page_returns_value():

    result = sdc_page()

    assert result is not None


def test_sdc_page_returns_expected_type():

    result = sdc_page()

    assert isinstance(
        result,
        (dict, list, bool, str, int, float)
    )
