from gocddash.analysis.data_access import get_connection
from gocddash.analysis.go_client import get_client
from gocddash.util.html_utils import remove_excessive_whitespace, clean_html


class JunitConsoleParser:
    def __init__(self, pipeline_name, pipeline_counter, stage_index, stage_name, job_name):
        success, response = get_client().go_request_junit_report(pipeline_name, pipeline_counter, stage_index,
                                                                 stage_name, job_name)
        self.console_log = response
        self.success = success

    def parse_info(self):
        if "Artifact 'testoutput/index.html' is unavailable as it may have been purged by Go or deleted externally." not in self.console_log:
            failure_information = self.extract_failure_info(self.console_log)
        else:
            failure_information = None

        return failure_information

    def parse_bar_chart_info(self):
        if self.success:
            return self.extract_bar_chart_data(self.console_log)
        else:
            return 0, 0, 0

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
                get_connection().insert_junit_failure_information(stage_id, error[0], error[1])

    def extract_bar_chart_data(self, console_log):
        console_log = console_log.split("Unit Test Failure and Error Details")[0]
        splitted_console_log_list = remove_excessive_whitespace(clean_html(console_log)).split()
        total_tests_run = splitted_console_log_list[2]
        failures = splitted_console_log_list[5]
        not_run = splitted_console_log_list[9]
        return total_tests_run, failures, not_run


if __name__ == '__main__':
    test = JunitConsoleParser('paysol-feature-tests', 2064, 1, 'runTests', 'defaultJob')
    print(test.parse_bar_chart_info())
