"""
This module handles the pipelines.json file and creates a PipelineConfig object from it.
"""
from gocddash.analysis.data_access import get_connection


class PipelineConfig:
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


def get_pipeline_config():
    return PipelineConfig()

