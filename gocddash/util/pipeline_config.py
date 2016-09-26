"""
This module handles the pipelines.json file and creates a PipelineConfig object from it.
"""
import codecs
import json
import os
from pathlib import Path
from ..console_parsers.determine_parser import get_parser_info


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
        with codecs.open(path, encoding="utf-8") as pipelines_json:
            try:
                self.pipelines = json.load(pipelines_json)
            except ValueError as err:
                print('TODO: Present Error Message about failed json parsing', err)
                raise

    def get_log_parser(self, pipeline_name):
        for config_dict in self.pipelines["pipelines"]:
            if pipeline_name == config_dict["name"]:
                return get_parser_info(config_dict.get('log_parser', None))
        return None

    def get_email_notif(self, pipeline_name):
        for config_dict in self.pipelines["pipelines"]:
            if pipeline_name == config_dict["name"]:
                return config_dict.get('email_notifications', False)
        return None


def create_pipeline_config(path=None):
    return PipelineConfig(path or str(Path(__file__).parents[1]) + "/pipelines.json")


def get_pipeline_config():
    return PipelineConfig()

