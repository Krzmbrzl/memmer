from typing import Optional
from typing import get_type_hints, get_args

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
import json


class ConfigKey(Enum):
    CONNECT_TYPE = "connector_type"
    DB_BACKEND = "connector_db_backend"
    DB_USER = "connector_db_user"
    DB_HOST = "connector_db_host"
    DB_PORT = "connector_db_port"
    DB_NAME = "connector_db_name"
    SSH_USER = "connector_ssh_user"
    SSH_PORT = "connector_ssh_port"
    SSH_KEY = "connector_ssh_key"

    TALLY_DIR = ("tally_out_dir",)


class ConnectType(Enum):
    REGULAR = "Regular"
    SSH_TUNNEL = "SSH-Tunnel"


class DBBackend(Enum):
    SQLite = "SQLite"
    MySQL = "MySQL"
    PostgreSQL = "PostgreSQL"


@dataclass
class MemmerConfig:
    connect_type: Optional[ConnectType] = None
    db_backend: Optional[DBBackend] = None
    db_user: Optional[str] = None
    db_host: Optional[str] = None
    db_port: Optional[int] = None
    db_name: Optional[str] = None
    ssh_user: Optional[str] = None
    ssh_port: Optional[int] = None
    ssh_key: Optional[str] = None

    tally_dir: Optional[str] = None

    def __getitem__(self, key: ConfigKey):
        return getattr(self, str(key.value))

    def __setitem__(self, key: ConfigKey, value):
        # TODO: ensure that value is of the expected type
        # and/or do necessary conversion from string
        setattr(self, str(key.value), value)


default_config_path: Path = Path.joinpath(Path.home(), ".memmer_config.json")


def load_config(config_path: Path = default_config_path) -> MemmerConfig:
    if not Path.is_file(config_path):
        return MemmerConfig()

    with open(config_path, "r") as config_file:
        try:
            config_json = json.load(config_file)
        except Exception as e:
            raise RuntimeError(f"Config file at '{config_path}' is malformed: {e}")

    config = MemmerConfig()
    config_types = get_type_hints(config)

    for key in ConfigKey:
        json_key = key.value
        member_name = key.name.lower()

        if not json_key in config_json:
            continue

        value = config_json[json_key]
        expected_type = config_types[member_name]

        args = get_args(expected_type)
        assert len(args) == 2
        args = [x for x in args if x is not type(None)]
        assert len(args) == 1
        expected_type = args[0]

        if value != None and value != "":
            config[key] = expected_type(value)
        else:
            config[key] = None

    return config


def save_config(config: MemmerConfig, config_path: Path = default_config_path):
    json_config = {}

    for key in ConfigKey:
        json_key = key.value

        value = config[key]

        if isinstance(value, Enum):
            json_config[json_key] = value.value
        else:
            json_config[json_key] = str(value)

    with open(config_path, "w") as config_file:
        json.dump(json_config, config_file)
