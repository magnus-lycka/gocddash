from gocddash.analysis.go_client import *
from gocddash.util.pipeline_config import get_pipeline_config


def get_failure_stage(pipeline_name, pipeline_id, stage, stage_name, job_name):
    success, response = go_request_junit_report(pipeline_name, pipeline_id, stage, stage_name, job_name)
    if success:
        log_parser = get_pipeline_config().get_log_parser(pipeline_name)
        if check_if_started(response):
            return "STARTUP"
        elif check_if_post_test(response):
            return "POST"
        elif check_test_failures(response, log_parser):
            return "TEST"
        else:
            return "UNKNOWN"
    else:
        return "STARTUP"


def check_if_started(text):
    return "No Tests Run" in text


def check_test_failures(text, log_parser):
    if log_parser == 'characterize':
        return "----------" in text
    elif log_parser == 'junit':
        return "Failures: 0" not in text


def check_if_post_test(text):
    return "All Tests Passed" in text
