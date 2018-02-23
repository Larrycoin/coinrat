import logging
from typing import Dict, Union

from decimal import Decimal

CONFIGURATION_STRUCTURE_TYPE_STRING = 'string'
CONFIGURATION_STRUCTURE_TYPE_INT = 'int'
CONFIGURATION_STRUCTURE_TYPE_DECIMAL = 'Decimal'
CONFIGURATION_STRUCTURE_TYPE_CANDLE_SIZE = 'candle_size'

logger = logging.getLogger(__name__)


def format_data_to_python_types(
    data: Dict[str, str],
    configuration_structure: Dict[str, Dict[str, str]]
) -> Dict[str, Union[str, int, Decimal]]:
    result: Dict[str, Union[str, int, Decimal]] = {}

    for key, value in data.items():
        if key not in configuration_structure:
            logger.warning('{} not expected by configuration structure definition'.format(key))
            continue

        structure = configuration_structure[key]

        is_nullable = structure['type'].startswith('?')

        if is_nullable and value is None:
            result[key] = None

        elif structure['type'] == CONFIGURATION_STRUCTURE_TYPE_INT:
            result[key] = int(value)

        elif structure['type'] == CONFIGURATION_STRUCTURE_TYPE_DECIMAL:
            result[key] = Decimal(value)

        else:
            result[key] = value

    return result
