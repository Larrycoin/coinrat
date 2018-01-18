from typing import Dict, Union

from decimal import Decimal

CONFIGURATION_STRUCTURE_TYPE_STRING = 'string'
CONFIGURATION_STRUCTURE_TYPE_INT = 'int'
CONFIGURATION_STRUCTURE_TYPE_DECIMAL = 'Decimal'


def format_data_to_python_types(
    data: Dict[str, str],
    configuration_structure: Dict[str, Dict[str, str]]
) -> Dict[str, Union[str, int, Decimal]]:
    for key, value in data.items():
        if key not in configuration_structure:
            raise ValueError('{} not expected by configuration structure definition'.format(key))

        structure = configuration_structure[key]

        if structure['type'] == CONFIGURATION_STRUCTURE_TYPE_INT:
            data[key] = int(value)

        if structure['type'] == CONFIGURATION_STRUCTURE_TYPE_DECIMAL:
            data[key] = Decimal(value)

    return data
