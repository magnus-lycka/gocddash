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
            self.pipelines = json.load(pipelines_json)

    def get_log_parser(self, pipeline_name):
        for config_dict in self.pipelines["pipelines"]:
            if pipeline_name == config_dict["name"]:
                return config_dict["log_parser"]
        return None


_pipeline_config = None


def create_pipeline_config(path=str(Path(__file__).parents[1]) + "/pipelines.json"):
    global _pipeline_config
    if not _pipeline_config:
        _pipeline_config = PipelineConfig(path)
        return _pipeline_config
    raise ValueError("PipelineConfig already instantiated - will not instantiate again.")


def get_config():
    if not _pipeline_config:
        raise ValueError("Pipeline config not instantiated")
    return _pipeline_config
