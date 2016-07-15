from ..analysis.data_munging import get_failure_stage_signature
from ..analysis.data_access import get_junit_failure_signature
from ..util.config import PipelineConfig


class StageSuccess:
    def __init__(self, stage):
        self.stage = stage

    def is_success(self):
        return True

    def describe_run_outcome(self):
        return "Success"

    def describe_rerun(self):
        return "Test was a success. Do not rerun."


class StageFailure(StageSuccess):
    def __init__(self, stage):
        StageSuccess.__init__(self, stage)

    def is_success(self):
        return False

    def describe_run_outcome(self):
        return "Failure"

    def describe_rerun(self):
        if self.stage.failure_stage == "POST":
            desc = "Tests failed at POST. Recommend to rerun tests."
        elif self.stage.failure_stage == "STARTUP":
            desc = "Tests failed during STARTUP. Recommend to rerun tests."
        else:
            desc = "Failure during TEST phase. Suspected flickering. Recommend to rerun tests."
        return desc

    def get_failure_stage_desc(self):
        return self.stage.failure_stage == "POST" or self.stage.failure_stage == "STARTUP"

    def has_error_statistics(self):
        return False


class TestFailure(StageFailure):
    def __init__(self, stage, failure_signature, test_names):
        StageFailure.__init__(self, stage)
        self.failure_signature = failure_signature
        self.test_names = test_names

    def __repr__(self):
        return "{} {} {} {} {}".format(self.stage.pipeline_name, self.stage.pipeline_counter, self.stage.stage_index,
                                       self.test_names, self.failure_signature)

    def has_error_statistics(self):
        return True


def create_stage_info(stage):
    log_parser = PipelineConfig().get_log_parser(stage.pipeline_name)

    if stage.is_success():
        result = StageSuccess(stage)

    # TODO: Think about this
    elif stage.failure_stage == "TEST" and log_parser == "characterize":
        failure_signatures_and_index_dict = get_failure_stage_signature(stage.stage_id)
        failure_signatures = failure_signatures_and_index_dict.values()
        failure_indices = failure_signatures_and_index_dict[stage.stage_id].keys()
        result = TestFailure(stage, failure_signatures, failure_indices)

    elif stage.failure_stage == "TEST" and log_parser == "junit":
        failure_tuples = get_junit_failure_signature(stage.stage_id)
        failure_signatures = [item[0] for item in failure_tuples]
        failure_indices = [item[1] for item in failure_tuples]
        result = TestFailure(stage, failure_signatures, failure_indices)

    else:
        result = StageFailure(stage)
    return result