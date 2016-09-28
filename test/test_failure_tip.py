import unittest
from unittest.mock import MagicMock

from gocddash.analysis.domain import StageFailureInfo
from gocddash.dashboard import failure_tip
from gocddash.dashboard import pipeline_status
from gocddash.util.pipeline_config import create_pipeline_config
from gocddash.console_parsers.characterize_console_parser import TexttestConsoleParser


class TestFailureTip(unittest.TestCase):
    path = "data/pipelines.json"
    create_pipeline_config(path)

    @staticmethod
    def create_stage_failure_info(parent=None, passed=False, failure_stage=None, stage_id=2000):
        if parent:
            pipeline_counter = parent.pipeline_counter - 1
        else:
            pipeline_counter = 2000

        return StageFailureInfo('characterize', pipeline_counter, 1, stage_id, "runTests", "triggered by x",
                                "changes", "Passed" if passed else "Failed", failure_stage, "resp", "desc", 2014)

    def test_current_passing(self):
        pipeline_status.get_log_parser = MagicMock(return_value="characterize")

        passed_stage = self.create_stage_failure_info(None, True)
        current = pipeline_status.create_stage_info(passed_stage)
        result = failure_tip.get_failure_tip(current, None, 0)
        self.assertEqual(result, ("All good.", ''))

    def test_current_startup(self):
        startup_stage = self.create_stage_failure_info(None, False, "STARTUP")
        current = pipeline_status.create_stage_info(startup_stage)
        result = failure_tip.get_failure_tip(current, None, 0)
        self.assertEqual(result, ("Tests failed during STARTUP.", ''))

    def test_current_post(self):
        post_stage = self.create_stage_failure_info(None, False, "POST")
        current = pipeline_status.create_stage_info(post_stage)
        result = failure_tip.get_failure_tip(current, None, 0)
        self.assertEqual(result, ("All tests passed, but the build failed.", ''))

    def test_error_introduced(self):
        pipeline_status.get_failure_stage_signature = MagicMock(return_value={2000: {}})
        pipeline_status.get_log_parser = MagicMock(return_value=TexttestConsoleParser)

        failed_stage = self.create_stage_failure_info(None, False, "TEST")
        passed_stage = self.create_stage_failure_info(failed_stage, True)
        current = pipeline_status.create_stage_info(failed_stage)
        previous = pipeline_status.create_stage_info(passed_stage)
        result = failure_tip.get_failure_tip(current, previous, 0)
        self.assertEqual(result,
                         ("Last pipeline was a success. Potential for flickering but may need further investigation.",
                          "Last claim: resp: desc")
                         )

    def test_error_unchanged(self):
        pipeline_status.get_failure_stage_signature = MagicMock(side_effect=[{2000: {}}, {1999: {}}])
        pipeline_status.get_log_parser = MagicMock(return_value=TexttestConsoleParser)

        this_stage = self.create_stage_failure_info(None, False, "TEST", stage_id=2000)
        previous_stage = self.create_stage_failure_info(this_stage, False, "TEST", stage_id=1999)
        current = pipeline_status.create_stage_info(this_stage)
        previous = pipeline_status.create_stage_info(previous_stage)
        result = failure_tip.get_failure_tip(current, previous, 0)
        self.assertEqual(result, ("Same failure indices as last test. Unlikely flickering.", "Last claim: resp: desc"))
