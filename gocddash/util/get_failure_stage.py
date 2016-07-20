from gocddash.analysis.go_client import *
from gocddash.util.config import get_config


def get_failure_stage(pipeline_name, pipeline_id, stage, stage_name, job_name):
    response = go_request_junit_report(pipeline_name, pipeline_id, stage, stage_name, job_name)
    log_parser = get_config().get_log_parser(pipeline_name)

    if check_if_started(response):
        return "STARTUP"
    elif check_if_post_test(response):
        return "POST"
    elif check_test_failures(response, log_parser):
        return "TEST"
    else:
        return "UNKNOWN"


def check_if_started(text):
    return "No Tests Run" in text


def check_test_failures(text, log_parser):
    if log_parser == 'characterize':
        return "----------" in text
    elif log_parser == 'junit':
        return "Failures: 0" not in text


def check_if_post_test(text):
    return "All Tests Passed" in text
