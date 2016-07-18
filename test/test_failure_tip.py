import unittest
from unittest.mock import MagicMock

from gocddash.analysis.domain import Stage
from gocddash.dash_board import failure_tip
from gocddash.dash_board import pipeline_status
from gocddash.util.config import create_config


class TestFailureTip(unittest.TestCase):
    create_config()

    def create_stage(self, parent=None, passed=False, failure_stage=None):
        if parent:
            pipeline_counter = parent.pipeline_counter - 1
        else:
            pipeline_counter = 2000

        return Stage("characterize", pipeline_counter, "triggered by x",
                     "changes", 1, "", "agent-123", failure_stage, "Passed" if passed else "Failed", pipeline_counter,
                     "runTests")

    def test_current_passing(self):

        passed_stage = self.create_stage(None, True)
        current = pipeline_status.create_stage_info(passed_stage)
        result = failure_tip.get_failure_tip(current, None, 0)
        self.assertEqual(result, "All good.")

    def test_current_startup(self):
        startup_stage = self.create_stage(None, False, "STARTUP")
        current = pipeline_status.create_stage_info(startup_stage)
        result = failure_tip.get_failure_tip(current, None, 0)
        self.assertEqual(result, "Tests failed during STARTUP.")

    def test_current_post(self):
        post_stage = self.create_stage(None, False, "POST")
        current = pipeline_status.create_stage_info(post_stage)
        result = failure_tip.get_failure_tip(current, None, 0)
        self.assertEqual(result, "All tests passed, but the build failed.")

    def test_error_introduced(self):
        pipeline_status.get_failure_stage_signature = MagicMock(return_value={2000: {}})

        failed_stage = self.create_stage(None, False, "TEST")
        passed_stage = self.create_stage(failed_stage, True)
        current = pipeline_status.create_stage_info(failed_stage)
        previous = pipeline_status.create_stage_info(passed_stage)
        result = failure_tip.get_failure_tip(current, previous, 0)
        self.assertEqual(result, "Last pipeline was a success. Suspected flickering.")

    def test_error_unchanged(self):
        pipeline_status.get_failure_stage_signature = MagicMock(side_effect=[
            {2000: {}}, {1999: {}}
        ])
        pipeline_status.get_config().get_log_parser = MagicMock(return_value="characterize")

        this_stage = self.create_stage(None, False, "TEST")
        previous_stage = self.create_stage(this_stage, False, "TEST")
        current = pipeline_status.create_stage_info(this_stage)
        previous = pipeline_status.create_stage_info(previous_stage)
        result = failure_tip.get_failure_tip(current, previous, 0)
        self.assertEqual(result, "Same failure indices as last test. Unlikely flickering.")
