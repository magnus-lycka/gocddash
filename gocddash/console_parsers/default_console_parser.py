"""Serves as an interface for the two different console parsers (characterize and JUnit)"""


class DefaultConsoleParser:
    # noinspection PyUnusedLocal
    def __init__(self, pipeline_name, pipeline_counter, stage_index, stage_name, job_name):
        self.console_log = None
        self.response = None
        self.success = True

    def insert_info(self, stage_id):  # pragma: no cover
        raise NotImplementedError

    def get_failure_stage(self):
        if self.success:
            if "No Tests Run" in self.response:
                return "STARTUP"
            elif "All Tests Passed" in self.response:
                return "POST"
            elif self._check_test_failures():
                return "TEST"
            else:
                return "UNKKNOWN"
        else:
            return "STARTUP"

    def _check_test_failures(self):  # pragma: no cover
        raise NotImplementedError
