
import pytest

from generated_components.pass_port_data_to_reporting import (
    pass_port_data_to_reporting
)


def test_pass_port_data_to_reporting_returns_value():

    result = pass_port_data_to_reporting()

    assert result is not None


def test_pass_port_data_to_reporting_returns_expected_type():

    result = pass_port_data_to_reporting()

    assert isinstance(
        result,
        (dict, list, bool, str, int, float)
    )
