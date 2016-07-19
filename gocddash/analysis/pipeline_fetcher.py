import json
from datetime import datetime

from gocddash.console_parsers.determine_parser import get_parser_info
from gocddash.util.get_failure_stage import get_failure_stage
from gocddash.util.config import get_config
from .data_access import get_connection
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
        if pipeline["stages"][0]["result"] != "Unknown":
            print("Now fetching pipeline: " + str(pipeline_counter))
            stage_count = pipeline["stages"][0]["counter"]
            pipeline_name = pipeline["name"]
            pipeline_id = pipeline["id"]
            stage_name = pipeline["stages"][0]["name"]
            get_connection().insert_pipeline(pipeline_id, stage_count, pipeline_name, pipeline_counter,
                            pipeline["build_cause"]["trigger_message"])
            parse_stage_info(stage_count, pipeline_name, pipeline_counter, stage_name)
        else:
            print("This pipeline index (" + str(pipeline_counter) + ") is not finished yet.")
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


def parse_stage_info(stage_count, pipeline_name, pipeline_counter, stage_name):
    for stageIndex in range(int(stage_count), 0, -1):
        response = go_request_stages_history(pipeline_name, pipeline_counter, stageIndex, stage_name)
        tree = json.loads(response)
        timestamp = ms_timestamp_to_date(tree["jobs"][0]["scheduled_date"]).replace(microsecond=0)
        stageid = tree["id"]
        stage_result = tree["result"]
        get_connection().insert_stage(stageid, tree["approved_by"], pipeline_counter, pipeline_name, stageIndex, stage_result, timestamp,
                     tree["jobs"][0]["agent_uuid"], stage_name)

        fetch_failure_info(stageIndex, pipeline_counter, pipeline_name, stage_result, stageid, stage_name)


def fetch_failure_info(stage_index, pipeline_counter, pipeline_name, stage_result, stage_id, stage_name):
    if stage_result == "Failed" and not get_connection().is_failure_downloaded(stage_id):

        log_parser = get_config().get_log_parser(pipeline_name)

        failure_stage = get_failure_stage(pipeline_name, pipeline_counter, stage_index, stage_name)
        get_connection().insert_failure_information(stage_id, failure_stage)

        failures = get_parser_info(log_parser)(pipeline_name, pipeline_counter, stage_index, stage_name)
        failures.insert_info(stage_id)


def ms_timestamp_to_date(ms):
    return datetime.fromtimestamp(ms / 1000.0)
