import json
from datetime import datetime

from console_parsers.determine_parser import get_parser_info
from util.config import PipelineConfig
from .data_access import *
from .get_failure_stage import get_failure_stage
from .go_client import *


def request_pipelines(pipeline_name, offset):
    pipeline_request = go_request_pipeline_history(pipeline_name, offset)
    if (pipeline_request.status_code == 200):
        return pipeline_request.content.decode("utf-8")
    else:
        return None


def download_and_store(pipeline_name, offset, run_times):
    pipeline_json = []
    for _ in range(run_times):
        pipelines = request_pipelines(pipeline_name, offset)
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
            insert_pipeline(pipeline_id, stage_count, pipeline_name, pipeline_counter,
                            pipeline["build_cause"]["trigger_message"])
            parse_stage_info(stage_count, pipeline_name, pipeline_counter, stage_name)
        else:
            print("This pipeline index (" + str(pipeline_counter) + ") is not finished yet.")
    fetch_new_agents()


def fetch_new_agents():
    new_agents = get_new_agents()
    for agent in new_agents:
        hostname = agent_uuid_to_hostname(agent)
        insert_agent(agent, hostname)


def agent_uuid_to_hostname(agent_uuid):
    agent_information = go_get_agent_information(agent_uuid)
    if agent_information.status_code == 404:
        return "UNKNOWN:" + agent_uuid
    return json.loads(agent_information.content.decode("utf-8"))["hostname"]


def parse_stage_info(stage_count, pipeline_name, pipeline_counter, stage_name):
    for i in range(int(stage_count), 0, -1):
        response = go_request_stages_history(pipeline_name, pipeline_counter, i, stage_name).decode("utf-8")
        tree = json.loads(response)
        timestamp = ms_timestamp_to_date(tree["jobs"][0]["scheduled_date"]).replace(microsecond=0)
        stageid = tree["id"]
        stage_result = tree["result"]
        insert_stage(stageid, tree["approved_by"], pipeline_counter, pipeline_name, i, stage_result, timestamp,
                     tree["jobs"][0]["agent_uuid"], stage_name)

        fetch_failure_info(i, pipeline_counter, pipeline_name, stage_result, stageid, stage_name)


def fetch_failure_info(stage_index, pipeline_counter, pipeline_name, stage_result, stage_id, stage_name):
    if stage_result == "Failed" and not is_failure_downloaded(stage_id):

        log_parser = PipelineConfig().get_log_parser(pipeline_name)

        failure_stage = get_failure_stage(pipeline_name, pipeline_counter, stage_index, stage_name)
        insert_failure_information(stage_id, failure_stage)

        failures = get_parser_info(log_parser)(pipeline_name, pipeline_counter, stage_index, stage_name)
        failures.insert_info(stage_id)


def ms_timestamp_to_date(ms):
    return datetime.fromtimestamp(ms / 1000.0)
