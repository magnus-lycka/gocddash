"""This module handles the application.cfg file and creates an AppConfig object from it.
Makes it easier to access configurations throughout the project.

"""
from flask import Config


class AppConfig(Config):
    _shared_state = {'root_path': None}

    def __init__(self, root_path=None, defaults=None):
        self.__dict__ = self._shared_state
        if root_path is not None:
            self._init(root_path, defaults)

    def _init(self, root_path, defaults):
        super().__init__(root_path, defaults)
        if defaults:
            self.from_object(defaults)
        self.from_envvar('APP_CONFIG')
        self.cfg = self


def create_app_config(path=None):
    return AppConfig(path or "application.cfg")


def get_app_config():
    return AppConfig()
