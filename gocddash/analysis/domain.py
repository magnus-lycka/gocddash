from .data_access import get_connection


def get_previous_stage(pipeline_name, pipeline_counter, current_stage_index):
    result = get_connection().fetch_previous_stage(pipeline_name, pipeline_counter, current_stage_index)
    if result:
        return StageFailureInfo(*result)
    else:
        return None


def get_current_stage(pipeline_name):
    result = get_connection().fetch_current_stage(pipeline_name)
    if result:
        return StageFailureInfo(*result)
    return None


def get_latest_passing_stage(pipeline_name):
    result = get_connection().fetch_latest_passing_stage(pipeline_name)
    if result:
        return StageFailureInfo(*result)
    else:
        return None


def create_stage(pipeline_instance, stage):
    get_connection().insert_stage(pipeline_instance.instance_id, stage)

class PipelineInstance:
    def __init__(self, pipeline_name, pipeline_counter, trigger_message, instance_id):
        self.pipeline_name = pipeline_name
        self.pipeline_counter = pipeline_counter
        self.trigger_message = trigger_message
        self.instance_id = instance_id
        self.stages = {}


class Stage:
    def __init__(self, stage_name, approved_by, stage_result, stage_counter, stage_id):
        self.stage_name = stage_name
        self.approved_by = approved_by
        self.stage_result = stage_result
        self.stage_counter = stage_counter
        self.stage_id = stage_id

    def is_success(self):
        return self.stage_result == "Passed"


class StageFailureInfo:
    def __init__(self, pipeline_name, pipeline_counter, stage_counter, stage_id, stage_name, trigger_message, approved_by, result, failure_stage):
        self.pipeline_name = pipeline_name
        self.pipeline_counter = pipeline_counter
        self.stage_id = stage_id
        self.stage_name = stage_name
        self.trigger_message = trigger_message
        self.approved_by = approved_by
        self.stage_index = stage_counter
        self.failure_stage = failure_stage # Should be moved to job
        self.result = result

    def is_success(self):
        return self.result == "Passed"


class Job:
    def __init__(self, job_name, agent_uuid, scheduled_date, job_id, job_result):
        self.job_name = job_name
        self.agent_uuid = agent_uuid
        self.scheduled_date = scheduled_date
        self.job_id = job_id
        self.job_result = job_result
