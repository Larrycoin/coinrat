from typing import Dict


def serialize_configuration_structure(structure: Dict[str, type]) -> Dict[str, str]:
    serialized_structure = {}
    for key, value in structure.items():
        serialized_structure[key] = value.__name__

    return serialized_structure
