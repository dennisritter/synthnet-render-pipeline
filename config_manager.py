"""Validates configuration files by checking it against a defined schema."""
import json
import jsonschema


def is_valid(config_json: object, schema: object) -> bool:
    """ Validates configuration files by checking it against a defined schema and
        prints an errors if the configuration file is not valid according to the schema.
        Args:
            config_json (JSON Object): The config to validate.
            schema (JSON Object): The config schema to validate against
    """
    jsonschema.validate(instance=config_json, schema=schema)


def load_config(config_path: str):
    """ Returns a render config json object that is valid according to the config schema.
        Args:
            config_path (str): Path to the config.json
    """
    SCHEMA_REL_PATH = './schemas/config_schema.json'
    with open(SCHEMA_REL_PATH, 'r', encoding='UTF-8') as json_file:
        cfg_schema = json.loads(json_file.read())

    with open(config_path, 'r', encoding='UTF-8') as config_json:
        cfg = json.loads(config_json.read())

    is_valid(cfg, cfg_schema)
    return cfg


cfg_global = load_config('./data/configs/example_global_scene.json')
cfg_part_scenes = load_config('./data/configs/example_part_scenes.json')
