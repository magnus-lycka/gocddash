"""Module used for parsing the console log of a characterize classified pipeline"""
import re

from gocddash.analysis.data_access import get_connection
from gocddash.analysis.go_client import go_request_console_log

ansi_escape = re.compile(r'\x1b[^m]*m')


class TexttestConsoleParser:
    def __init__(self, pipeline_name, pipeline_counter, stage_index, stage_name, job_name):
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
            test_case = ansi_escape.sub('', test_case)

            send_error = [error for error in failure_case_list if test_case + " " in error]
            error_list = self.extract_failure_info(send_error)

            if error_list:
                for i, item in enumerate(error_list):
                    error_list[i] = (index + 1,) + item

            test_dict[test_case] = error_list

        final_dict = {key: value for (key, value) in test_dict.items() if value is not None}
        return final_dict

    @staticmethod
    def extract_failure_info(failure_case):
        if failure_case:
            error = failure_case[0]
            error_codes = error.split(': ', 1)[1]

            error_list = [category for category in error_codes.split(', ')]

            type_document_error_list = []

            for category in error_list:

                if ',' in category:
                    for document in category.split(','):
                        type_document_error_list.append(
                            (category.split()[0], ansi_escape.sub('', document.split()[-1])))
                else:
                    type_document_error_list.append((category.split()[0], ansi_escape.sub('', category.split()[-1])))

            return type_document_error_list
        else:
            return None

    def insert_info(self, stage_id):
        failures = self.parse_info()
        if failures:
            for key, value in failures.items():
                for failure in value:
                    index, failure_type, document_name = failure
                    get_connection().insert_texttest_failure(stage_id, index, failure_type, document_name)
