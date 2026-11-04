
"""
Voyager RF Link Budget Calculator

Uses published Voyager S-band and X-band specifications to calculate RF link-budget parameters.

No physical spacecraft measurements are generated.

"""

import math

from spacecraft_config import VOYAGER_RF_SYSTEMS


# Speed of light in metres per second
SPEED_OF_LIGHT = 299_792_458


def watts_to_dbw(power_w):
    #Convert power in watts to dBW.

    if power_w <= 0:
        raise ValueError("Power must be greater than zero.")

    return 10 * math.log10(power_w)


def dbw_to_dbm(power_dbw):
    #Convert power in dBW to dBm.

    return power_dbw + 30


def calculate_eirp(transmitter_power_w, antenna_gain_dbi):
    """
    Calculate effective isotropic radiated power (EIRP).

    EIRP (dBW) = Transmitter power (dBW) + Antenna gain (dBi)
    """

    transmitter_power_dbw = watts_to_dbw(transmitter_power_w)

    eirp_dbw = transmitter_power_dbw + antenna_gain_dbi

    return {
        "transmitter_power_w": transmitter_power_w,
        "transmitter_power_dbw": transmitter_power_dbw,
        "eirp_dbw": eirp_dbw,
        "eirp_dbm": dbw_to_dbm(eirp_dbw)
    }


def calculate_free_space_path_loss(frequency_mhz, distance_km):
    """
    Calculate free-space path loss (FSPL).

    FSPL = 20 log10(4 * pi * distance / wavelength)

    Distance must be supplied in kilometres and the frequency must be supplied in MHz.
    """

    if frequency_mhz <= 0:
        raise ValueError("Frequency must be greater than zero.")

    if distance_km <= 0:
        raise ValueError("Distance must be greater than zero.")

    frequency_hz = frequency_mhz * 1_000_000
    distance_m = distance_km * 1_000

    wavelength_m = SPEED_OF_LIGHT / frequency_hz

    path_loss_db = 20 * math.log10(
        (4 * math.pi * distance_m) / wavelength_m
    )

    return path_loss_db


def calculate_link_budget(
    system,
    transmitter_power_w,
    distance_km,
    receiver_antenna_gain_dbi,
    system_losses_db,
    receiver_sensitivity_dbm=None
):
    """
    Calculate the received signal power and optional link margin.

    Received power =
        EIRP - Free-space path loss
        + receiver antenna gain - system losses

    Link margin =
        Received power - receiver sensitivity
    """

    if distance_km <= 0:
        raise ValueError("Distance must be greater than zero.")

    if system_losses_db < 0:
        raise ValueError("System losses cannot be negative.")

    if transmitter_power_w not in system.transmitter_power_options_w:
        raise ValueError(
            "Transmitter power must match a configured Voyager power option."
        )

    eirp = calculate_eirp(
        transmitter_power_w,
        system.high_gain_antenna_gain_dbi
    )

    path_loss_db = calculate_free_space_path_loss(
        system.transmit_frequency_mhz,
        distance_km
    )

    received_power_dbm = (
        eirp["eirp_dbm"]
        - path_loss_db
        + receiver_antenna_gain_dbi
        - system_losses_db
    )

    link_margin_db = None

    if receiver_sensitivity_dbm is not None:
        link_margin_db = (
            received_power_dbm - receiver_sensitivity_dbm
        )

    return {
        "system": system.name,
        "frequency_mhz": system.transmit_frequency_mhz,
        "distance_km": distance_km,
        "transmitter_power_w": transmitter_power_w,
        "transmitter_power_dbw": eirp["transmitter_power_dbw"],
        "eirp_dbw": eirp["eirp_dbw"],
        "eirp_dbm": eirp["eirp_dbm"],
        "free_space_path_loss_db": path_loss_db,
        "receiver_antenna_gain_dbi": receiver_antenna_gain_dbi,
        "system_losses_db": system_losses_db,
        "received_power_dbm": received_power_dbm,
        "receiver_sensitivity_dbm": receiver_sensitivity_dbm,
        "link_margin_db": link_margin_db
    }


def display_eirp_results(system):
    #Display EIRP for each available transmitter power option for the given system.

    print("\n" + "=" * 50)
    print(f"{system.name.upper()} TRANSMITTER ANALYSIS")
    print("=" * 50)

    for power in system.transmitter_power_options_w:

        result = calculate_eirp(
            power,
            system.high_gain_antenna_gain_dbi
        )

        print(f"\nTransmitter power: {power} W")
        print(
            f"Transmitter power: "
            f"{result['transmitter_power_dbw']:.2f} dBW"
        )
        print(f"EIRP: {result['eirp_dbw']:.2f} dBW")
        print(f"EIRP: {result['eirp_dbm']:.2f} dBm")


if __name__ == "__main__":

    print("VOYAGER RF LINK BUDGET ANALYSIS")

    for system in VOYAGER_RF_SYSTEMS.values():
        display_eirp_results(system)
