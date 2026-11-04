
"""
Voyager Mission RF Link Budget Analysis that uses published Voyager spacecraft RF specifications and Date-stamped Voyager-to-Earth distance estimates derived from NASA/JPL Horizons ephemeride

Receiver antenna gain and additional losses are set to zero for this initial free-space reference calculation.

This is not a complete operational DSN link budget.
"""

from spacecraft_config import VOYAGER_RF_SYSTEMS
from link_budget import calculate_link_budget


# Ephemeris-derived distance estimates, November 4, 2026
# Source: NASA/JPL Horizons calculations
VOYAGER_DISTANCES_KM = {
    "Voyager 1": 25_866_422_766,
    "Voyager 2": 21_640_220_298
}


# Initial reference assumptions:
# Isotropic receiving antenna = 0 dBi
# No additional system losses included
RECEIVER_ANTENNA_GAIN_DBI = 0.0
SYSTEM_LOSSES_DB = 0.0


def run_mission_analysis():

    print("=" * 65)
    print("Voyager Spacecraft RF Link Budget Analysis")
    print("Reference date: November 4, 2026")
    print("=" * 65)

    for spacecraft, distance_km in VOYAGER_DISTANCES_KM.items():

        print(f"\nSpacecraft: {spacecraft}")
        print(f"Distance from Earth: {distance_km:,} km")

        for system in VOYAGER_RF_SYSTEMS.values():

            print("\n" + "-" * 55)
            print(f"{system.name.upper()} LINK ANALYSIS")
            print("-" * 55)

            for power in system.transmitter_power_options_w:

                result = calculate_link_budget(
                    system=system,
                    transmitter_power_w=power,
                    distance_km=distance_km,
                    receiver_antenna_gain_dbi=(
                        RECEIVER_ANTENNA_GAIN_DBI
                    ),
                    system_losses_db=SYSTEM_LOSSES_DB
                )

                print(f"\nTransmitter power: {power} W")

                print(
                    f"EIRP: "
                    f"{result['eirp_dbw']:.2f} dBW"
                )

                print(
                    f"Free-space path loss: "
                    f"{result['free_space_path_loss_db']:.2f} dB"
                )

                print(
                    f"Received power (isotropic reference): "
                    f"{result['received_power_dbm']:.2f} dBm"
                )


if __name__ == "__main__":
    run_mission_analysis()
