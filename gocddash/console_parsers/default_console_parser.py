"""Serves as an interface for the two different console parsers (characterize and JUnit)"""


class DefaultConsoleParser:
    def __init__(self, console_log):
        raise NotImplementedError

    def insert_info(self, stage_id):
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

    def _check_test_failures(self):
        raise NotImplementedError
