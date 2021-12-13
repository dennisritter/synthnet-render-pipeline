"""Validates configuration files by checking it against a defined schema."""
import os
import json
import jsonschema
from jsonschema.validators import RefResolver



def is_valid(config_json: object, schema: object, resolver) -> bool:
    """ Validates configuration files by checking it against a defined schema and
        prints an errors if the configuration file is not valid according to the schema.
        Args:
            config_json (JSON Object): The config to validate.
            schema (JSON Object): The config schema to validate against
    """
    jsonschema.validate(instance=config_json, schema=schema, resolver=resolver)

def load_config(config_path: str):
    """ Returns a render config json object.
        Args:
            config_path (str): Path to the config.json
    """
    SCHEMA_REL_PATH = './schemas/config_schema.json'
    SCHEMA_ABS_PATH = f"file://{os.path.dirname(os.path.abspath(SCHEMA_REL_PATH))}"
    with open(SCHEMA_REL_PATH, 'r', encoding='UTF-8') as json_file:
        cfg_schema = json.load(json_file)
    with open(config_path, 'r', encoding='UTF-8') as config_json:
        cfg = json.load(config_json)
    resolver = RefResolver(SCHEMA_ABS_PATH, cfg_schema)
    is_valid(cfg, cfg_schema, resolver=resolver)
    return cfg

load_config('./data/configs/example_global_scene.json')
