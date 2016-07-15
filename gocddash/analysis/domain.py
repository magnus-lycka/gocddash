from .data_access import get_connection


class Stage:
    def __init__(self, pipeline_name, pipeline_counter, trigger_message, approved_by, stage_index, scheduled_date,
                 agent_name, failure_stage, result, stage_id, stage_name):
        self.pipeline_name = pipeline_name
        self.pipeline_counter = pipeline_counter
        self.trigger_message = trigger_message
        self.approved_by = approved_by
        self.stage_index = stage_index
        self.scheduled_date = scheduled_date
        self.agent_name = agent_name
        self.failure_stage = failure_stage
        self.result = result
        self.stage_id = stage_id
        self.stage_name = stage_name

    def is_success(self):
        return self.result == "Passed"


def get_previous_stage(pipeline_name, pipeline_counter, current_stage_index):
    result = get_connection().fetch_previous_stage(pipeline_name, pipeline_counter, current_stage_index)
    if result:
        return Stage(*result)
    else:
        return None


def get_current_stage(pipeline_name):
    result = get_connection().fetch_current_stage(pipeline_name)
    if result:
        return Stage(*result)
    return None


def get_latest_passing_stage(pipeline_name):
    result = get_connection().fetch_latest_passing_stage(pipeline_name)
    if result:
        return Stage(*result)
    else:
        return None
