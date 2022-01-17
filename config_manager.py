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
    SCHEMA_REL_PATH = './validation/schemas/rcfg_schema_v2.json'
    with open(SCHEMA_REL_PATH, 'r', encoding='UTF-8') as json_file:
        cfg_schema = json.loads(json_file.read())

    with open(config_path, 'r', encoding='UTF-8') as config_json:
        cfg = json.loads(config_json.read())

    is_valid(cfg, cfg_schema)
    return cfg


def get_base_config():
    """ Returns a minimal, empty base config that validates against the schema.
    """
    CFG_BASE_DEFAULT_PATH = './cfg/cfg_base_default.json'
    return load_config(CFG_BASE_DEFAULT_PATH)


# Just a quick test whether loading and validation work with the examples
# cfg_global = load_config('./cfg/cfg_example_global_scene.json')
# cfg_part_scenes = load_config('./cfg/cfg_example_part_scenes.json')
# cfg_base_default = get_base_config()
# print(cfg_base_default)
