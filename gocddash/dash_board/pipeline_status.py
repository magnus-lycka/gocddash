from ..analysis.data_access import get_connection
from ..analysis.data_munging import get_failure_stage_signature
from ..util.pipeline_config import get_pipeline_config


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


def create_stage_info(stage_failure_info):
    log_parser = get_pipeline_config().get_log_parser(stage_failure_info.pipeline_name)
    if log_parser is None:  # Log parser should almost always be junit. This fixes changing config without reloading the cfg
        log_parser = 'junit'
    if stage_failure_info.is_success():
        result = StageSuccess(stage_failure_info)
    elif stage_failure_info.failure_stage == "TEST":
        result = failure_extractors[log_parser](stage_failure_info)
    else:
        result = StageFailure(stage_failure_info)
    return result


def junit_failure_extraction(stage_failure_info):
    failure_tuples = get_connection().get_junit_failure_signature(stage_failure_info.stage_id)
    failure_signatures = [item[0] for item in failure_tuples]
    failure_indices = [item[1] for item in failure_tuples]
    return TestFailure(stage_failure_info, failure_signatures, failure_indices)


def characterize_failure_extraction(stage_failure_info):
    failure_signatures_and_index_dict = get_failure_stage_signature(stage_failure_info.stage_id)
    failure_signatures = failure_signatures_and_index_dict.values()
    failure_indices = failure_signatures_and_index_dict[stage_failure_info.stage_id].keys()
    return TestFailure(stage_failure_info, failure_signatures, failure_indices)


failure_extractors = {
    "characterize": characterize_failure_extraction,
    "junit": junit_failure_extraction
}
