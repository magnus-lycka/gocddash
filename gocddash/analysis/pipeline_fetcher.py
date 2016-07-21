import json
from datetime import datetime

from gocddash.console_parsers.determine_parser import get_parser_info
from gocddash.util.config import get_config
from gocddash.util.get_failure_stage import get_failure_stage
from .data_access import get_connection
from .domain import PipelineInstance, Stage, create_stage, Job, create_job
from .go_client import *


def download_and_store(pipeline_name, offset, run_times):
    pipeline_json = []
    for _ in range(run_times):
        pipelines = go_request_pipeline_history(pipeline_name, offset)
        if pipelines:
            pipeline_json.extend(json.loads(pipelines)["pipelines"])
            offset += 10
        else:
            print("Could not get pipeline history from GO.")

    parse_pipeline_info(pipeline_json)


def parse_pipeline_info(pipelines):
    for pipeline in pipelines:
        pipeline_counter = pipeline["counter"]
        for stage in pipeline['stages']:
            if stage['scheduled']:
                stage_name = stage['name']
                if stage['result'] != "Unknown":
                    print("Now fetching pipeline: {} | Stage: {}".format(pipeline_counter, stage_name))
                    pipeline_name = pipeline["name"]
                    pipeline_id = pipeline["id"]
                    stage_count = stage['counter']
                    instance = PipelineInstance(pipeline_name, pipeline_counter, pipeline["build_cause"]["trigger_message"], pipeline_id)
                    get_connection().insert_pipeline_instance(instance)
                    parse_stage_info(stage_count, stage_name, instance)
                else:
                    print("This pipeline index ({} | Stage: {}) is not finished yet.".format(pipeline_counter, stage_name))
    fetch_new_agents()


def fetch_new_agents():
    new_agents = get_connection().get_new_agents()
    for agent in new_agents:
        hostname = agent_uuid_to_hostname(agent)
        get_connection().insert_agent(agent, hostname)


def agent_uuid_to_hostname(agent_uuid):
    exists, agent_information = go_get_agent_information(agent_uuid)
    if not exists:
        return "UNKNOWN:" + agent_uuid
    return json.loads(agent_information)["hostname"]


def parse_stage_info(stage_count, stage_name, pipeline_instance):
    for stage_index in range(int(stage_count), 0, -1):
        pipeline_name = pipeline_instance.pipeline_name
        pipeline_counter = pipeline_instance.pipeline_counter

        response = go_request_stage_instance(pipeline_name, pipeline_counter, stage_index, stage_name)
        tree = json.loads(response)
        stageid = tree["id"]
        stage_result = tree["result"]
        timestamp = ms_timestamp_to_date(tree["jobs"][0]["scheduled_date"]).replace(microsecond=0)  # Leave for now but a Stage doesn't have a scheduled_date in the API

        stage = Stage(stage_name, tree["approved_by"], stage_result, stage_index, stageid, timestamp)
        create_stage(pipeline_instance, stage)

        for job in tree['jobs']:
            job_name = job['name']
            agent_uuid = job['agent_uuid']
            scheduled_date = ms_timestamp_to_date(job['scheduled_date']).replace(microsecond=0)
            job_id = job['id']
            job_result = job['result']
            job = Job(job_name, agent_uuid, scheduled_date, job_id, job_result)
            create_job(stage, job)

            fetch_failure_info(stage_index, pipeline_counter, pipeline_name, stage_result, stageid, stage_name, job_name)


def fetch_failure_info(stage_index, pipeline_counter, pipeline_name, stage_result, stage_id, stage_name, job_name):
    if stage_result == "Failed" and not get_connection().is_failure_downloaded(stage_id):

        log_parser = get_config().get_log_parser(pipeline_name)

        failure_stage = get_failure_stage(pipeline_name, pipeline_counter, stage_index, stage_name, job_name)
        get_connection().insert_failure_information(stage_id, failure_stage)

        failures = get_parser_info(log_parser)(pipeline_name, pipeline_counter, stage_index, stage_name, job_name)
        failures.insert_info(stage_id)


def ms_timestamp_to_date(ms):
    return datetime.fromtimestamp(ms / 1000.0)
