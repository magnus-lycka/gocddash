"""Module used for parsing the console log of a characterize classified pipeline"""
import re

from gocddash.analysis.data_access import get_connection
from gocddash.analysis.go_client import go_request_console_log
from gocddash.analysis.go_client import go_request_junit_report
from .default_console_parser import DefaultConsoleParser


def ansi_escape(x):
    return re.compile(r'\x1b[^m]*m').sub('', x)


class TexttestConsoleParser(DefaultConsoleParser):
    def __init__(self, pipeline_name, pipeline_counter, stage_index, stage_name, job_name):
        super().__init__(pipeline_name, pipeline_counter, stage_index, stage_name, job_name)
        self.success, self.response = go_request_junit_report(
            pipeline_name, pipeline_counter, stage_index, stage_name, job_name)
        self.console_log = go_request_console_log(pipeline_name, pipeline_counter, stage_index, stage_name, job_name)

    def parse_info(self):
        """
        Parses the console.log from GO.CD and indexes the test-cases in the order they were run
        :return: Dictionary in {Test_Name : [index, error_type, document]} form
        """
        console_log_start_split = self.console_log.split('Using Application', 1)[-1]
        console_log_split = console_log_start_split.split('Results:', 1)[0]
        test_case_list = [item for item in console_log_split.splitlines() if "Running" in item and "test-case" in item]
        failure_case_list = [item for item in console_log_split.splitlines() if "FAILED" in item]

        test_dict = {}

        for index, test_row in enumerate(test_case_list):
            test_case = test_row.split('test-case', 1)[-1]
            test_case = ansi_escape(test_case)

            send_error = [error for error in failure_case_list if test_case + " " in error]
            error_list = self.extract_failure_info(send_error)

            for i, item in enumerate(error_list):
                error_list[i] = (index + 1,) + item

            test_dict[test_case] = error_list

        final_dict = {key: value for (key, value) in test_dict.items() if value}
        return final_dict

    @staticmethod
    def extract_failure_info(failure_case):
        type_document_error_list = []
        if failure_case:
            error = failure_case[0]
            error_codes = error.split(': ', 1)[1]

            error_list = [category for category in error_codes.split(', ')]
            for category in error_list:
                for document in category.split(','):
                    type_document_error_list.append(
                        (category.split()[0], ansi_escape(document.split()[-1])))
        return type_document_error_list

    def insert_info(self, stage_id):
        failures = self.parse_info()
        if failures:
            for value in failures.values():
                for failure in value:
                    index, failure_type, document_name = failure
                    get_connection().insert_texttest_failure(stage_id, index, failure_type, document_name)

    def _check_test_failures(self):
        return len(self.parse_info()) > 0
