
"""
Voyager Spacecraft RF Configuration

Reference data:
NASA Planetary Data System (PDS)
Voyager Radio Science Subsystem documentation.

These are educational reference values for the Voyager spacecraft RF systems.
"""

from dataclasses import dataclass
from typing import Tuple


@dataclass
class RFSystem:
    #Stores the published RF characteristics of a Voyager radio band.

    name: str
    transmit_frequency_mhz: float
    transmitter_power_options_w: Tuple[float, ...]
    high_gain_antenna_gain_dbi: float
    antenna_half_power_beamwidth_deg: float
    polarization: str


# Voyager S-band communications system
S_BAND = RFSystem(
    name="S-band",
    transmit_frequency_mhz=2296.0,
    transmitter_power_options_w=(9.0, 26.0),
    high_gain_antenna_gain_dbi=36.0,
    antenna_half_power_beamwidth_deg=1.1,
    polarization="Right-hand circular"
)


# Voyager X-band communications system
X_BAND = RFSystem(
    name="X-band",
    transmit_frequency_mhz=8415.0,
    transmitter_power_options_w=(12.0, 22.0),
    high_gain_antenna_gain_dbi=47.0,
    antenna_half_power_beamwidth_deg=0.32,
    polarization="Circular (right-hand or left-hand)"
)


# Both RF systems available for testing
VOYAGER_RF_SYSTEMS = {
    "S-band": S_BAND,
    "X-band": X_BAND
}


# Source documentation
DATA_SOURCE = (
    "NASA Planetary Data System - Voyager Radio Science Subsystem"
)

DATA_SOURCE_URL = (
    "https://pds-rings.seti.org/voyager/rss/vg1sinst.html"
)


def display_system_configuration(system: RFSystem) -> None:
    #Print the configuration of a given Voyager RF system.

    print("\n" + "=" * 45)
    print(f"VOYAGER {system.name.upper()} CONFIGURATION")
    print("=" * 45)

    print(f"Transmit frequency: "
          f"{system.transmit_frequency_mhz} MHz")

    print(f"Available transmitter powers: "
          f"{system.transmitter_power_options_w} W")

    print(f"High-gain antenna gain: "
          f"{system.high_gain_antenna_gain_dbi} dBi")

    print(f"Half-power beamwidth: "
          f"{system.antenna_half_power_beamwidth_deg} degrees")

    print(f"Polarization: {system.polarization}")


if __name__ == "__main__":

    print("Voyager Spacecraft RF System Configuration")
    print(f"Data source: {DATA_SOURCE}")

    for system in VOYAGER_RF_SYSTEMS.values():
        display_system_configuration(system)
