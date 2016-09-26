"""
This module handles the pipelines.json file and creates a PipelineConfig object from it.
It makes it easier to access configurations throughout the project.
"""
import codecs
import json
import os
from pathlib import Path


class PipelineConfig:
    def __init__(self, path):
        self.path = path
        if not os.path.isfile(path):
            raise FileNotFoundError("Error: Missing pipelines.json file in {}".format(path))
        with codecs.open(path, encoding="utf-8") as pipelines_json:
            try:
                self.pipelines = json.load(pipelines_json)
            except ValueError as err:
                print('TODO: Present Error Message about failed json parsing', err)
                raise

    def get_log_parser(self, pipeline_name):
        for config_dict in self.pipelines["pipelines"]:
            if pipeline_name == config_dict["name"]:
                return config_dict.get('log_parser', None)
        return None

    def get_email_notif(self, pipeline_name):
        for config_dict in self.pipelines["pipelines"]:
            if pipeline_name == config_dict["name"]:
                return config_dict.get('email_notifications', False)
        return None

_pipeline_config = None


def create_pipeline_config(path=None):
    if not path:
        path = str(Path(__file__).parents[1]) + "/pipelines.json"
    global _pipeline_config
    if not _pipeline_config:
        _pipeline_config = PipelineConfig(path)
        return _pipeline_config
    else:
        path = _pipeline_config.path
        _pipeline_config = PipelineConfig(path)
        return _pipeline_config


def get_pipeline_config():
    if not _pipeline_config:
        raise ValueError("Pipeline config not instantiated")
    return _pipeline_config

