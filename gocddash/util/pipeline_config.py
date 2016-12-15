"""
This module handles the pipelines.json file and creates a PipelineConfig object from it.
"""
from gocddash.analysis.data_access import get_connection


class PipelineConfig:
    @staticmethod
    def get_log_parser_name(pipeline_name):
        pipeline = get_connection().get_pipeline(pipeline_name)
        return pipeline['log_parser']

    @staticmethod
    def get_email_notif(pipeline_name):
        pipeline = get_connection().get_pipeline(pipeline_name)
        return pipeline['email_notifications']
