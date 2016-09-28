"""
Extracts the failure stage of a pipeline from the JUnit report.
"""

from gocddash.console_parsers.determine_parser import get_log_parser


def get_failure_stage(pipeline_name, pipeline_id, stage, stage_name, job_name):
    log_parser_class = get_log_parser(pipeline_name)
    log_parser = log_parser_class(pipeline_name, pipeline_id, stage, stage_name, job_name)
    return log_parser.get_failure_stage()
