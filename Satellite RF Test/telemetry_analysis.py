
"""
Voyager Telemetry Performance Analysis that uses the ground_station.py link analysis model to calculate C/N0 and Eb/N0 for various telemetry data rates.

Uses:
- Voyager X-band downlink configuration
- DSN 70-metre reference ground station
- Published Voyager telemetry data rates

Calculates:
- Carrier-to-noise density ratio (C/N0)
- Energy per bit to noise density ratio (Eb/N0)

This is an educational link analysis, not live telemetry.
"""

import math

from ground_station import analyze_downlink


# Voyager 1 distance estimate, November 4, 2026
VOYAGER_1_DISTANCE_KM = 25_866_422_766

# Published Voyager telemetry rates
TELEMETRY_DATA_RATES = {
    "Normal real-time telemetry": 160,
    "High-rate playback": 1400,
    "Maximum documented science rate": 7200
}

# Voyager X-band high-power transmitter setting
TRANSMITTER_POWER_W = 22.0


def calculate_eb_n0(c_n0_db_hz, data_rate_bps):
    """
    Calculate energy per bit to noise density ratio.

    Eb/N0 = C/N0 - 10*log10(data rate)

    Returns Eb/N0 in dB.
    """

    if data_rate_bps <= 0:
        raise ValueError("Data rate must be positive.")

    eb_n0_db = (
        c_n0_db_hz - 10 * math.log10(data_rate_bps)
    )

    return eb_n0_db


def analyze_telemetry():

    # Calculate the ground-station link once
    link_results = analyze_downlink(
        distance_km=VOYAGER_1_DISTANCE_KM,
        transmitter_power_w=TRANSMITTER_POWER_W
    )

    c_n0 = link_results[
        "carrier_to_noise_density_db_hz"
    ]

    print("=" * 65)
    print("Voyager Telemetry Performance Analysis")
    print("=" * 65)

    print(f"\nSpacecraft: Voyager 1")
    print(f"Distance: {VOYAGER_1_DISTANCE_KM:,} km")
    print(f"Transmitter power: {TRANSMITTER_POWER_W} W")

    print(
        f"Ground station C/N0: {c_n0:.2f} dB-Hz"
    )

    print("\n" + "-" * 65)
    print("Telemetry Data Rate Analysis")
    print("-" * 65)

    for mode, data_rate in TELEMETRY_DATA_RATES.items():

        eb_n0 = calculate_eb_n0(
            c_n0,
            data_rate
        )

        print(f"\nOperating mode: {mode}")

        print(f"Data rate: {data_rate:,} bits/second")

        print(f"Data rate: {data_rate / 1000:.3f} kbps")

        print(f"C/N0: {c_n0:.2f} dB-Hz")

        print(f"Eb/N0: {eb_n0:.2f} dB")

    print("\n" + "=" * 65)
    print("End of analysis")
    print("=" * 65)


if __name__ == "__main__":
    analyze_telemetry()
