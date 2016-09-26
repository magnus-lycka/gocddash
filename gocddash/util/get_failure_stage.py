"""
Extracts the failure stage of a pipeline from the JUnit report.
"""

from gocddash.util.pipeline_config import get_pipeline_config


def get_failure_stage(pipeline_name, pipeline_id, stage, stage_name, job_name):
    log_parser_class = get_pipeline_config().get_log_parser(pipeline_name)
    log_parser = log_parser_class(pipeline_name, pipeline_id, stage, stage_name, job_name)
    return log_parser.get_failure_stage()
