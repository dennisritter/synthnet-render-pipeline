"""Validates configuration files by checking it against a defined schema."""

import json
import jsonschema


with open('./schemas/config_schema.json', 'r') as json_file:
    CFG_SCHEMA = json.load(json_file)

def is_valid(config_json: object) -> bool:
    """ Validates configuration files by checking it against a defined schema. 
        Returns True if the given config is valid an False if it's not. 
    Args:
        config_json (JSON Object): The config to validate.
    """
    return jsonschema.validate(instance=config_json, schema=CFG_SCHEMA)

