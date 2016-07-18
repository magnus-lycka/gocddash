import codecs
import json
import os
from pathlib import Path


def singleton(cls):
    instances = {}

    def get_instance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]

    return get_instance


@singleton
class PipelineConfig:
    def __init__(self):
        if not os.path.isfile(str(Path(__file__).parents[1]) + "/pipelines.json"):
            print("Error: Missing pipelines.json file!")
            quit()
        with codecs.open(str(Path(__file__).parents[1]) + "/pipelines.json", encoding="utf-8") as pipelines_json:
            self.pipelines = json.load(pipelines_json)

    def get_log_parser(self, pipeline_name):
        for config_dict in self.pipelines["pipelines"]:
            if pipeline_name == config_dict["name"]:
                return config_dict["log_parser"]
        return None

    def get_auth(self):
        return self.pipelines["username"], self.pipelines["password"]


if __name__ == '__main__':
    test = PipelineConfig()
