"""This module handles the application.cfg file and creates an AppConfig object from it.
Makes it easier to access configurations throughout the project.

"""
from pathlib import Path
from flask import Config
import os


class AppConfig(Config):
    def __init__(self, root_path, defaults=None):
        super().__init__(root_path, defaults)
        if defaults:
            self.from_object(defaults)
        self.from_envvar('APP_CONFIG')
        self.cfg = self

_app_config = None


def create_app_config(path=None):
    if not path:
        path = str(Path(__file__).parents[1]) + "/application.cfg"
    global _app_config
    _app_config = AppConfig(path)
    return _app_config


def get_app_config():
    if not _app_config:
        raise ValueError("Application config not instantiated")
    return _app_config
