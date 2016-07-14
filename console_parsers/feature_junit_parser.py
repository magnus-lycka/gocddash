from analysis.data_access import insert_junit_failure_information
from analysis.go_client import go_request_junit_report
from console_parsers.html_utils import *



class JunitConsoleParser:
    def __init__(self, pipeline_name, pipeline_counter, stage_index, stage_name):
        self.console_log = go_request_junit_report(pipeline_name, pipeline_counter, stage_index, stage_name)

    def parse_info(self):
        if "Artifact 'testoutput/index.html' is unavailable as it may have been purged by Go or deleted externally." not in self.console_log:
            failure_information = self.extract_failure_info(self.console_log)
        else:
            failure_information = None

        return failure_information

    def extract_failure_info(self, console_log):
        console_log = console_log.split("Unit Test Failure and Error Details")[0]
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
                insert_junit_failure_information(stage_id, error[0], error[1])
