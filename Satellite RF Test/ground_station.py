
"""
Deep Space Network Ground Station Model

Reference configuration:
70-metre DSN X-band receiving antenna with 20 K system noise temperature.

Published reference values:
- Antenna gain: 74.2 dBi
- System noise temperature: 20 K

These are historical published DSN reference specifications for educational link analysis.
No live telemetry is generated or used.
"""

import math

from dataclasses import dataclass

from spacecraft_config import X_BAND
from link_budget import calculate_link_budget


# Boltzmann constant in joules per kelvin
BOLTZMANN_CONSTANT = 1.380649e-23


@dataclass
class GroundStation:
    #Stores ground-station receiving characteristics.

    name: str
    antenna_diameter_m: float
    antenna_gain_dbi: float
    system_noise_temperature_k: float
    frequency_band: str


# Published 70-metre DSN X-band reference configuration
DSN_70M_X_BAND = GroundStation(
    name="DSN 70-metre Reference Antenna",
    antenna_diameter_m=70.0,
    antenna_gain_dbi=74.2,
    system_noise_temperature_k=20.0,
    frequency_band="X-band"
)


def calculate_gt(antenna_gain_dbi, noise_temperature_k):
    """
    Calculate antenna gain-to-system-noise-temperature ratio.

    G/T = Antenna gain (dBi) - 10*log10(system temperature)
    """

    if noise_temperature_k <= 0:
        raise ValueError("Noise temperature must be positive.")

    return antenna_gain_dbi - 10 * math.log10(
        noise_temperature_k
    )


def calculate_noise_density(noise_temperature_k):
    """
    Calculate thermal noise power spectral density.

    N0 = k * T

    Returns noise density in dBm/Hz.
    """

    if noise_temperature_k <= 0:
        raise ValueError("Noise temperature must be positive.")

    noise_density_w_per_hz = (
        BOLTZMANN_CONSTANT * noise_temperature_k
    )

    noise_density_dbm_per_hz = (
        10 * math.log10(noise_density_w_per_hz) + 30
    )

    return noise_density_dbm_per_hz


def analyze_downlink(
    distance_km,
    transmitter_power_w,
    system_losses_db=0.0
):
    """
    Estimate Voyager X-band downlink performance
    using the DSN 70-metre reference antenna.
    """

    link = calculate_link_budget(
        system=X_BAND,
        transmitter_power_w=transmitter_power_w,
        distance_km=distance_km,
        receiver_antenna_gain_dbi=(
            DSN_70M_X_BAND.antenna_gain_dbi
        ),
        system_losses_db=system_losses_db
    )

    gt_ratio = calculate_gt(
        DSN_70M_X_BAND.antenna_gain_dbi,
        DSN_70M_X_BAND.system_noise_temperature_k
    )

    noise_density = calculate_noise_density(
        DSN_70M_X_BAND.system_noise_temperature_k
    )

    carrier_to_noise_density = (
        link["received_power_dbm"] - noise_density
    )

    return {
        "ground_station": DSN_70M_X_BAND.name,
        "spacecraft": "Voyager 1",
        "frequency_mhz": X_BAND.transmit_frequency_mhz,
        "distance_km": distance_km,
        "transmitter_power_w": transmitter_power_w,
        "ground_antenna_gain_dbi": (
            DSN_70M_X_BAND.antenna_gain_dbi
        ),
        "system_noise_temperature_k": (
            DSN_70M_X_BAND.system_noise_temperature_k
        ),
        "gt_db_per_k": gt_ratio,
        "free_space_path_loss_db": (
            link["free_space_path_loss_db"]
        ),
        "received_power_dbm": (
            link["received_power_dbm"]
        ),
        "noise_density_dbm_per_hz": noise_density,
        "carrier_to_noise_density_db_hz": (
            carrier_to_noise_density
        )
    }


def display_results(results):

    print("\n" + "=" * 60)
    print("Voyager X-Band Downlink Performance Analysis")
    print("=" * 60)

    print(f"Spacecraft: {results['spacecraft']}")
    print(f"Ground station: {results['ground_station']}")

    print(f"\nFrequency: {results['frequency_mhz']} MHz")

    print(
        f"Distance: {results['distance_km']:,} km"
    )

    print(
        f"Transmitter power: "
        f"{results['transmitter_power_w']} W"
    )

    print("\nGROUND STATION")

    print(
        f"Antenna gain: "
        f"{results['ground_antenna_gain_dbi']:.2f} dBi"
    )

    print(
        f"System noise temperature: "
        f"{results['system_noise_temperature_k']:.2f} K"
    )

    print(
        f"G/T: {results['gt_db_per_k']:.2f} dB/K"
    )

    print("\nLINK PERFORMANCE")

    print(
        f"Free-space path loss: "
        f"{results['free_space_path_loss_db']:.2f} dB"
    )

    print(
        f"Received signal power: "
        f"{results['received_power_dbm']:.2f} dBm"
    )

    print(
        f"Noise density: "
        f"{results['noise_density_dbm_per_hz']:.2f} dBm/Hz"
    )

    print(
        f"C/N0: "
        f"{results['carrier_to_noise_density_db_hz']:.2f} dB-Hz"
    )


if __name__ == "__main__":

    # Voyager 1 distance estimate used in our previous analysis
    voyager_1_distance_km = 25_866_422_766

    # Use the 22 W X-band transmitter setting
    results = analyze_downlink(
        distance_km=voyager_1_distance_km,
        transmitter_power_w=22.0
    )

    display_results(results)
