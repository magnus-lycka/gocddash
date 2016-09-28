"""
This module handles the pipelines.json file and creates a PipelineConfig object from it.
"""
import json
import os
import sys


class PipelineConfig:
    _shared_state = {'path': None}

    def __init__(self, path=None):
        self.__dict__ = self._shared_state
        if path is not None:
            self._init(path)

    def _init(self, path):
        self.path = path
        if not os.path.isfile(path):
            raise FileNotFoundError("Error: Missing pipelines.json file in {}".format(path))
        with open(path, encoding="utf-8") as pipelines_json:
            try:
                self.pipelines = json.load(pipelines_json)
                print("Loaded new pipeline configuration from {}.".format(path), file=sys.stderr)
            except ValueError as err:
                print('ERROR: Failed parsing json file {},'.format(path), err)
                raise

    def get_log_parser_name(self, pipeline_name):
        for config_dict in self.pipelines["pipelines"]:
            if pipeline_name == config_dict["name"]:
                return config_dict.get('log_parser', None)

    def get_email_notif(self, pipeline_name):
        for config_dict in self.pipelines["pipelines"]:
            if pipeline_name == config_dict["name"]:
                return config_dict.get('email_notifications', False)


def create_pipeline_config(path):
    return PipelineConfig(path)


def get_pipeline_config():
    return PipelineConfig()

