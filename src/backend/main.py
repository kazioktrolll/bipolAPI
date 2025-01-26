from .physics import get_density, get_mach, G


def create_run_file(constrains:dict[str, tuple[str, float]], parameters:dict[str, float]) -> str:
    """
    Generate data in .run file format.

    Transform given constrains and parameters into a .run file formatted text.

    :param constrains: A dict in format {'alpha': ('alpha', 0)}.
    :param parameters: A dict in format {'velocity': 0}.
    :return: String with formatted data.
    """
    base_constrains = {'alpha': ('alpha', 0.0),
                       'beta': ('beta', 0.0),
                       'pb/2V': ('pb/2V', 0.0),
                       'qc/2V': ('qc/2V', 0.0),
                       'rb/2V': ('rb/2V', 0.0),}
    base_parameters = {'velocity': 0.0,
                       'altitude': 0.0}

    constrains = base_constrains | constrains   # Overwrite default, append additional
    parameters = base_parameters | parameters   # Same here

    run_file_parameters = {'grav.acc.': (G, 'm/s^2'),
                           'density': (get_density(parameters['altitude']), 'kg/m^3'),
                           'velocity': (parameters['velocity'], 'm/s'),
                           'Mach': (get_mach(parameters['velocity'], parameters['altitude']), '')}

    constructed_string = 'Run case  1: AutoCase\n'
    for k, v in constrains.items():
        constructed_string += f'{k} -> {v[0]} = {v[1]}\n'

    constructed_string += '\n'

    for k, v in run_file_parameters.items():
        constructed_string += f'{k} = {v[0]} {v[1]}\n'

    return constructed_string