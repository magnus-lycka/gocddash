"""
This module handles the pipelines.json file and creates a PipelineConfig object from it.
"""
from gocddash.analysis.data_access import get_connection


class PipelineConfig:
    _shared_state = {'path': None}

    def __init__(self, path=None):
        pass

    @staticmethod
    def get_log_parser_name(pipeline_name):
        for pipeline in get_connection().list_pipelines():
            if pipeline_name == pipeline["pipeline_name"]:
                return pipeline['log_parser']

    @staticmethod
    def get_email_notif(pipeline_name):
        for pipeline in get_connection().list_pipelines():
            if pipeline_name == pipeline["pipeline_name"]:
                return pipeline.get['email_notifications']


def create_pipeline_config(path):
    return PipelineConfig(path)


def get_pipeline_config():
    return PipelineConfig()

