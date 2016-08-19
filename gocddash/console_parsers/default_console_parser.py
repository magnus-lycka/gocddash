"""Serves as an interface for the two different console parsers (characterize and JUnit)"""


class DefaultConsoleParser:
    def __init__(self, console_log):
        self.console_log = console_log

    def insert_info(self, stage_id):
        pass
