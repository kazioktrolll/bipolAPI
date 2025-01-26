from math import exp


G = 9.80665 # m/s^2
T0 = 288.15 # K
P0 = 101325 # Pa
R = 287.05  # J/kg*K


def get_temperature(altitude: float) -> float:
    """
    Calculate temperature at a given altitude.
    :param altitude: Altitude in meters.
    :return: Temperature in Kelvins.
    """
    assert 20e3 > altitude >= 0
    if altitude == 0: return T0
    L = -6.5e-3
    if altitude <= 11e3: return T0 + L * altitude
    return get_temperature(11e3)


def get_pressure(altitude: float) -> float:
    """
    Calculate pressure at a given altitude.
    :param altitude: Altitude in meters.
    :return: Pressure in pascals.
    """
    assert 20e3 > altitude >= 0
    if altitude == 0: return P0
    if altitude <= 11e3: return P0 * (get_temperature(altitude) / T0)**(-G / R / altitude)
    return get_pressure(11e3) * exp((-G * (altitude - 11e3)) / (R * get_temperature(altitude)))


def get_density(altitude:float) -> float:
    """
    Calculate density at a given altitude.
    :param altitude: Altitude in meters.
    :return: Air density in kg/m^3.
    """
    assert 20e3 > altitude >= 0
    return get_pressure(altitude) / get_temperature(altitude) / R


def get_mach(velocity:float, altitude:float=0.0) -> float:
    """
    Calculate Mach number at a given altitude.
    :param velocity: Velocity in m/s.
    :param altitude: Altitude in meters.
    :return: Mach number.
    """
    SHR_air = 1.4   # Specific heat ratio γ for air
    T = get_temperature(altitude)
    a = (SHR_air * R * T)**0.5
    return velocity / a
