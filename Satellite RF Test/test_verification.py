
import pytest
from verification import calculate_eb_n0, verify_link


def test_calculate_eb_n0_at_160_bps():
    #Check the expected Eb/N0 for normal telemetry.
    result = calculate_eb_n0(31.01, 160)

    assert result == pytest.approx(8.97, abs=0.01)


def test_calculate_eb_n0_decreases_as_data_rate_increases():
    #Higher data rates should have lower Eb/N0 at fixed C/N0.
    normal = calculate_eb_n0(31.01, 160)
    high_rate = calculate_eb_n0(31.01, 1400)

    assert high_rate < normal


def test_link_passes_when_margin_is_positive():
    #A result above the requirement should pass.
    result = verify_link(
        c_n0_db_hz=31.01,
        data_rate_bps=160,
        minimum_eb_n0_db=3.0,
    )

    assert result["passed"] is True
    assert result["margin"] > 0


def test_link_fails_when_margin_is_negative():
    #A result below the requirement should fail.
    result = verify_link(
        c_n0_db_hz=31.01,
        data_rate_bps=1400,
        minimum_eb_n0_db=3.0,
    )

    assert result["passed"] is False
    assert result["margin"] < 0


def test_link_passes_when_margin_is_exactly_zero():
    #Meeting the minimum requirement exactly should pass.
    result = verify_link(
        c_n0_db_hz=10.0,
        data_rate_bps=10,
        minimum_eb_n0_db=0.0,
    )

    assert result["margin"] == pytest.approx(0.0)
    assert result["passed"] is True



def test_zero_data_rate_is_rejected():
    #A zero data rate is invalid for the Eb/N0 calculation.
    with pytest.raises(ValueError):
        calculate_eb_n0(31.01, 0)


def test_negative_data_rate_is_rejected():
    #A negative data rate is invalid.
    with pytest.raises(ValueError):
        calculate_eb_n0(31.01, -160)
