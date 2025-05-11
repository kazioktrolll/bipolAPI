"""
Copyright (c) 2025 Wojciech Kwiatkowski

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
"""


from math import exp

G = 9.80665
"""int: Earth's gravita"""
T0 = 288.15  # K
P0 = 101325  # Pa
R = 287.05  # J/kg*K


def get_temperature(altitude: float) -> float:
    """
    Calculate temperature at a given altitude.
    Parameters:
        altitude (float): Altitude in meters.
    Returns:
        Temperature in Kelvins.
    """
    if not 20e3 > altitude >= 0: raise ValueError("Altitude must be between 0 and 20km!")
    if altitude == 0: return T0
    L = -6.5e-3
    if altitude <= 11e3: return T0 + L * altitude
    return get_temperature(11e3)


def get_pressure(altitude: float) -> float:
    """
    Calculate pressure at a given altitude.
    Parameters:
        altitude (float): Altitude in meters.
    Returns:
        Pressure in pascals.
    """
    if not 20e3 > altitude >= 0: raise ValueError("Altitude must be between 0 and 20km!")
    if altitude == 0: return P0
    if altitude <= 11e3: return P0 * (get_temperature(altitude) / T0) ** (-G / R / altitude)
    return get_pressure(11e3) * exp((-G * (altitude - 11e3)) / (R * get_temperature(altitude)))


def get_density(altitude: float) -> float:
    """
    Calculate density at a given altitude.
    Parameters:
        altitude (float): Altitude in meters.
    Returns:
        Air density in kg/m^3.
    """
    return get_pressure(altitude) / get_temperature(altitude) / R


def get_mach(velocity: float, altitude: float = 0.0) -> float:
    """
    Calculate Mach number at a given altitude.
    Parameters:
        velocity (float): Velocity in m/s.
        altitude (float): Altitude in meters.
    Returns:
        Mach number.
    """
    SHR_air = 1.4  # Specific heat ratio γ for air
    T = get_temperature(altitude)
    a = (SHR_air * R * T) ** 0.5
    return velocity / a
