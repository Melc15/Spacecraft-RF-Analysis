
"""
Voyager Spacecraft RF Link Verification that calculates Eb/N0 for different telemetry data rates, compares against a minimum Eb/N0 threshold, calculates the available performance margin, and reports PASS or FAIL.

IMPORTANT: The 3 dB threshold is an educational example only and does not represent the official NASA requirement.

"""

import math

# 1. Verification configuration
# C/N0 calculated by our ground_station.py model.
# Units: dB-Hz
C_N0_DB_HZ = 31.01

# Educational example requirement, this is NOT an official NASA requirement!!
MINIMUM_EB_N0_DB = 3.0

# Telemetry scenarios (bits per second).
TELEMETRY_SCENARIOS = {
    "Normal real-time telemetry": 160,
    "High-rate playback": 1400,
    "Historical high-rate capability": 7200,
}

# 2. Calculate Eb/N0

def calculate_eb_n0(c_n0_db_hz, data_rate_bps):
    """
    Calculate energy per bit to noise density ratio.

    C/N0: carrier-to-noise density ratio (dB-Hz)
    Data rate: bits per second

    Returns Eb/N0 in dB.
    """

    if data_rate_bps <= 0:
        raise ValueError("Data rate must be greater than zero.")

    return c_n0_db_hz - 10 * math.log10(data_rate_bps)

# 3. Verify link against minimum Eb/N0 requirement


def verify_link(c_n0_db_hz, data_rate_bps, minimum_eb_n0_db):
    """
    Compare calculated Eb/N0 against the minimum requirement.

    Returns the calculated Eb/N0, margin, and test result.
    """

    eb_n0 = calculate_eb_n0(c_n0_db_hz, data_rate_bps)

    # Positive margin means the requirement is met.
    margin = eb_n0 - minimum_eb_n0_db

    passed = margin >= 0

    return {
        "eb_n0": eb_n0,
        "margin": margin,
        "passed": passed,
    }

# 4. Run verification for all scenarios and print results

def run_verification():

    print("=" * 65)
    print("Voyagere Spacecraft RF Link Verification")
    print("=" * 65)

    print("\nTest Configuration")
    print("-" * 65)

    print(f"Calculated C/N0:       {C_N0_DB_HZ:.2f} dB-Hz")
    print(f"Minimum Eb/N0:         {MINIMUM_EB_N0_DB:.2f} dB")
    print("Requirement source:    Educational example only")

    print("\nVerification Results")
    print("-" * 65)

    for scenario, data_rate in TELEMETRY_SCENARIOS.items():

        result = verify_link(
            C_N0_DB_HZ,
            data_rate,
            MINIMUM_EB_N0_DB
        )

        status = "PASS" if result["passed"] else "FAIL"

        print(f"\nScenario:       {scenario}")
        print(f"Data rate:      {data_rate:,} bits/s")
        print(f"Calculated Eb/N0: {result['eb_n0']:.2f} dB")
        print(f"Required Eb/N0:   {MINIMUM_EB_N0_DB:.2f} dB")
        print(f"Link margin:      {result['margin']:.2f} dB")
        print(f"Test result:      {status}")

    print("\n" + "=" * 65)
    print("Verification Results Summary")
    print("=" * 65)

    print(
        "\nNote: These are educational model results, "
        "not measurements of an operational Voyager link."
    )


# 5. Start the verification process

if __name__ == "__main__":
    run_verification()
