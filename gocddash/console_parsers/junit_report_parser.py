"""Module used for parsing the console log of a JUnit classified pipeline"""
from gocddash.analysis.data_access import get_connection
from gocddash.analysis.go_client import go_request_junit_report
from gocddash.util.html_utils import remove_excessive_whitespace, clean_html
from .default_console_parser import DefaultConsoleParser


# Traceback (most recent call last):
#   File "venv/bin/gocddash_sync.py", line 355, in <module>
#     controller.sync()
#   File "venv/bin/gocddash_sync.py", line 52, in sync
#     self.sync_pipelines()
#   File "venv/bin/gocddash_sync.py", line 107, in sync_pipelines
#     self.sync_pipeline(pipeline_name)
#   File "venv/bin/gocddash_sync.py", line 115, in sync_pipeline
#     self.sync_stages(pipeline_name, pipeline_instance)
#   File "venv/bin/gocddash_sync.py", line 137, in sync_stages
#     self.sync_stage(pipeline_name, pipeline_counter, pipeline_id, stage)
#   File "venv/bin/gocddash_sync.py", line 151, in sync_stage
#     stage_name, stage_counter)
#   File "venv/bin/gocddash_sync.py", line 175, in sync_stage_occurrence
#     self.sync_job(pipeline_name, pipeline_counter, stage_id, stage_name, stage_counter, job)
#   File "venv/bin/gocddash_sync.py", line 189, in sync_job
#     parser = JunitConsoleParser(pipeline_name, pipeline_counter, stage_counter, stage_name, job_name)
#   File "/var/www/gocddashtest/venv/lib/python3.4/site-packages/gocddash/console_parsers/junit_report_parser.py", line 11, in __init__
#     success, response = go_request_junit_report(pipeline_name, pipeline_counter, stage_index, stage_name, job_name)
#   File "/var/www/gocddashtest/venv/lib/python3.4/site-packages/gocddash/analysis/go_client.py", line 224, in go_request_junit_report
#     return _go_client.go_request_junit_report(pipeline_name, pipeline_id, stage, stage_name, job_name)
#   File "/var/www/gocddashtest/venv/lib/python3.4/site-packages/gocddash/analysis/go_client.py", line 112, in go_request_junit_report
#     request = self.base_request(template.format(pipeline_name, pipeline_id, stage_name, stage, job_name))
#   File "/var/www/gocddashtest/venv/lib/python3.4/site-packages/gocddash/analysis/go_client.py", line 58, in base_request
#     raise LookupError(err)
# LookupError: 404 Client Error: Not Found for url: http://localhost:8153/go/files/archive-feature-tests/2948/runTests/1/defaultJob/testoutput/index.html


class JunitConsoleParser(DefaultConsoleParser):
    def __init__(self, pipeline_name, pipeline_counter, stage_index, stage_name, job_name):
        super().__init__(pipeline_name, pipeline_counter, stage_index, stage_name, job_name)

        ###
        success, response = go_request_junit_report(pipeline_name, pipeline_counter, stage_index, stage_name, job_name)
        ###

        self.response = response
        self.console_log = response
        self.success = success

    def parse_info(self):
        if self.success:
            return self.extract_failure_info()

    def parse_bar_chart_info(self):
        if self.success:
            return self.extract_bar_chart_data()
        else:
            return 0, 0, 0

    def extract_failure_info(self):
        console_log = self.console_log.split("Unit Test Failure and Error Details")[0]
        console_log = remove_excessive_whitespace(clean_html(console_log))
        console_log = console_log.split("seconds.")[1]
        console_log = console_log.splitlines()

        console_log = [item.strip() for item in console_log if item and item != ' ']
        console_log = ["Failure " + item.split("Failure")[1] if "Failure" in item else item for item in
                       console_log]
        console_log = ["Error " + item.split("Error")[1] if "Error" in item else item for item in console_log]
        console_log = [(item.split(' ', 1)[0], item.split(' ', 1)[1]) for item in console_log]
        return console_log

    def insert_info(self, stage_id):
        failures = self.parse_info()
        if failures:
            for error in failures:
                get_connection().insert_junit_failure_information(stage_id, error[0], error[1])

    def extract_bar_chart_data(self):
        console_log = self.console_log.split("Unit Test Failure and Error Details")[0]
        splitted_console_log_list = remove_excessive_whitespace(clean_html(console_log)).split()
        total_tests_run = splitted_console_log_list[2]
        failures = splitted_console_log_list[5]
        not_run = splitted_console_log_list[9]
        return total_tests_run, failures, not_run

    def _check_test_failures(self):
        return "Failures: 0" not in self.console_log
