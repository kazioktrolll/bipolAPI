"""
Copyright (c) 2025 Wojciech Kwiatkowski

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
"""

import math

# Constants
g0 = 9.80665  # m/s^2
R_star = 8.31432  # J/(mol·K)
M = 0.0289644  # kg/mol
R = R_star / M  # Specific gas constant for air, J/(kg·K)
SHR_air = 1.4  # Specific heat ratio γ for air

# Define atmospheric layers (base altitude in km, base temperature in K, base pressure in Pa, lapse rate in K/km)
layers = [
    (0, 288.15, 101325.0, -6.5),
    (11, 216.65, 22632.06, 0.0),
    (20, 216.65, 5474.889, 1.0),
    (32, 228.65, 868.0187, 2.8),
    (47, 270.65, 110.9063, 0.0),
    (51, 270.65, 66.93887, -2.8),
    (71, 214.65, 3.956420, -2.0),
    (84.852, 186.946, 0.3734, 0.0)  # Up to 84.852 km
]


def get_temperature(h: float) -> float:
    """Calculate temperature at a given altitude, up to 80 km.

    :param h: Altitude in meters.
    :return: Temperature in Kelvins.
    """
    assert 0 <= h <= 8e4
    h_km = h / 1000
    for i in range(len(layers) - 1):
        h0, T0, _, L = layers[i]
        h1 = layers[i + 1][0]
        if h0 <= h_km < h1:
            return T0 + L * (h_km - h0)
    return layers[-1][1]  # Altitude exactly at top layer


def get_pressure(h: float) -> float:
    """Calculate pressure at a given altitude, up to 80 km.

    :param h: Altitude in meters.
    :return: Pressure in Pascals."""
    assert 0 <= h <= 8e4
    h_km = h / 1000
    for i in range(len(layers) - 1):
        h0, T0, P0, L = layers[i]
        h1 = layers[i + 1][0]
        if h0 <= h_km < h1:
            if L == 0:
                # Isothermal
                exponent = -g0 * M * (h_km - h0) * 1000 / (R_star * T0)
                return P0 * math.exp(exponent)
            else:
                # Gradient
                T = T0 + L * (h_km - h0)
                base = T0 / T
                exponent = (g0 * M) / (R_star * L * 1e-3)
                return P0 * base ** exponent
    return layers[-1][2]  # Altitude exactly at top layer


def get_density(h: float) -> float:
    """Returns air density at altitudes up to 80 km.

    :param h: Altitude above sea level in meters.
    :return: Air density in kg/m^3.
    """
    assert 0 <= h <= 8e4
    T = get_temperature(h)
    P = get_pressure(h)
    return P / (R * T)


def get_mach(velocity: float, altitude: float = 0.0) -> float:
    """
    Calculate Mach number at a given altitude, up to 80 km.
    Parameters:
        velocity (float): Velocity in m/s.
        altitude (float): Altitude in meters.
    Returns:
        Mach number.
    """
    assert 0 <= altitude <= 8e4
    T = get_temperature(altitude)
    a = (SHR_air * R * T) ** 0.5
    return velocity / a
