
import pytest

from generated_components.html_template import (
    html_template
)


def test_html_template_returns_value():

    result = html_template()

    assert result is not None


def test_html_template_returns_expected_type():

    result = html_template()

    assert isinstance(
        result,
        (dict, list, bool, str, int, float)
    )
