
import numpy as np
import pytest

from rf_test_system import (
    MINIMUM_ACCEPTABLE_GAIN_DB,
    evaluate_measurements,
    run_rf_test,
    simulate_rf_measurement,
    smoothstep,
    summarize_results,
)


def test_normal_operation_passes_all_measurements():
    results = run_rf_test(inject_fault=False)
    summary = summarize_results(results)

    assert summary["total_tests"] == 101
    assert summary["failed"] == 0
    assert summary["passed"] == 101
    assert summary["overall_result"] == "PASS"


def test_injected_fault_is_detected():
    results = run_rf_test(inject_fault=True)
    summary = summarize_results(results)

    assert summary["failed"] > 0
    assert summary["passed"] > 0
    assert summary["overall_result"] == "FAIL"


def test_fault_is_localized_to_expected_frequency_region():
    results = run_rf_test(inject_fault=True)

    failed_frequencies = [
        item["frequency_ghz"]
        for item in results
        if item["result"] == "FAIL"
    ]

    assert len(failed_frequencies) > 0
    assert all(1.78 <= f <= 2.22 for f in failed_frequencies)


def test_acceptance_threshold_is_inclusive():
    results = evaluate_measurements(
        frequencies_ghz=[1.0, 2.0, 3.0],
        gain_measurements_db=[
            MINIMUM_ACCEPTABLE_GAIN_DB - 0.1,
            MINIMUM_ACCEPTABLE_GAIN_DB,
            MINIMUM_ACCEPTABLE_GAIN_DB + 0.1,
        ],
    )

    assert [item["result"] for item in results] == [
        "FAIL",
        "PASS",
        "PASS",
    ]


def test_margin_is_calculated_correctly():
    results = evaluate_measurements(
        frequencies_ghz=[2.0],
        gain_measurements_db=[20.0],
    )

    assert results[0]["margin_db"] == pytest.approx(2.0)


def test_smoothstep_has_correct_endpoints():
    values = smoothstep(np.array([0.0, 0.5, 1.0]))

    assert values[0] == pytest.approx(0.0)
    assert values[1] == pytest.approx(0.5)
    assert values[2] == pytest.approx(1.0)


def test_invalid_measurement_lengths_are_rejected():
    with pytest.raises(ValueError):
        evaluate_measurements(
            frequencies_ghz=[1.0, 2.0],
            gain_measurements_db=[20.0],
        )


def test_empty_frequency_input_is_rejected():
    with pytest.raises(ValueError):
        simulate_rf_measurement(np.array([]))


def test_non_finite_measurements_are_rejected():
    with pytest.raises(ValueError):
        evaluate_measurements(
            frequencies_ghz=[1.0],
            gain_measurements_db=[float("nan")],
        )
