"""This module handles the application.cfg file and creates an AppConfig object from it.
Makes it easier to access configurations throughout the project.

"""

import os
from configparser import ConfigParser
from itertools import chain
from pathlib import Path


class AppConfig:
    def __init__(self, path):
        self.path = path
        if not os.path.isfile(path):
            raise FileNotFoundError("Error: Missing application.cfg file in {}".format(path))
        self.cfg = _read_from_file(path)

_app_config = None


def _read_from_file(path=None):
    if not path:
        path = os.getcwd() + "/gocddash/application.cfg"
    parser = ConfigParser()
    if not os.path.exists(path):
        raise FileNotFoundError("Error: Missing application.cfg file in {}".format(path))
    with open(path) as lines:
        lines = chain(("[top]",), lines)  # Reads cfg file without section headers
        parser.read_file(lines)

    cfg = dict(parser.items('top'))
    cfg = {key.strip('"').upper(): value.strip('"') for key, value in cfg.items()}
    return cfg


def create_app_config(path=None):
    if not path:
        path = str(Path(__file__).parents[1]) + "/application.cfg"
    global _app_config
    if not _app_config:
        _app_config = AppConfig(path)
        return _app_config
    else:
        path = _app_config.path
        _pipeline_config = AppConfig(path)
        return _pipeline_config


def get_app_config():
    if not _app_config:
        raise ValueError("Application config not instantiated")
    return _app_config
