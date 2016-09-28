"""Fetches all the relevant data from the synchronisation process and stores it in the database"""
import json
from datetime import datetime

from gocddash.console_parsers.junit_report_parser import JunitConsoleParser
from gocddash.util.get_failure_stage import get_failure_stage
from gocddash.util.pipeline_config import get_pipeline_config
from gocddash.console_parsers.determine_parser import get_log_parser
from .data_access import get_connection
from .domain import PipelineInstance, Stage, create_stage, Job, create_job
from .email_notifications import build_email_notifications
from .go_client import go_request_pipeline_history, go_get_agent_information, go_request_stage_instance


def download_and_store(pipeline_name, offset, run_times):
    pipeline_json = []
    for _ in range(run_times):
        pipelines = go_request_pipeline_history(pipeline_name, offset)
        if pipelines:
            pipeline_json.extend(json.loads(pipelines)["pipelines"])
            offset += 10
        else:
            print("Could not get pipeline history from GO.")

    parse_pipeline_info(pipeline_name, pipeline_json)


def parse_pipeline_info(pipeline_name, pipeline_instances):
    for pipeline in pipeline_instances:
        pipeline_counter = pipeline["counter"]
        print("Pipeline counter: {}".format(pipeline_counter))
        pipeline_id = pipeline["id"]
        instance = PipelineInstance(pipeline_name, pipeline_counter,
                                    pipeline["build_cause"]["trigger_message"], pipeline_id)
        if not get_connection().pipeline_instance_exists(pipeline_name, pipeline_counter):
            get_connection().insert_pipeline_instance(instance)

        for stage in pipeline['stages']:
            if stage['scheduled']:
                stage_name = stage['name']
                stage_count = stage['counter']
                parse_stage_info(stage_count, stage_name, instance)
    fetch_new_agents()
    send_new_email_notifications(pipeline_name)


def send_new_email_notifications(pipeline_name):
    if get_pipeline_config().get_email_notif(pipeline_name):
        build_email_notifications(pipeline_name)


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
    latest_synced_stage = get_connection().get_latest_synced_stage(pipeline_instance.instance_id, stage_name)
    for stage_index in range(int(stage_count), latest_synced_stage, -1):
        pipeline_name = pipeline_instance.pipeline_name
        pipeline_counter = pipeline_instance.pipeline_counter

        stage_instance_response = go_request_stage_instance(pipeline_name, pipeline_counter, stage_index, stage_name)
        tree = json.loads(stage_instance_response)
        stage_result = tree["result"]
        if stage_result != "Unknown":
            print("  Fetching stage: {} / {}".format(stage_name, stage_index))
            stage_id = tree["id"]

            # Leave for now but a Stage doesn't have a scheduled_date in the API
            timestamp = ms_timestamp_to_date(tree["jobs"][0]["scheduled_date"]).replace(microsecond=0)
            stage = Stage(stage_name, tree["approved_by"], stage_result, stage_index, stage_id, timestamp)
            create_stage(pipeline_instance, stage)

            fetch_job(pipeline_counter, pipeline_name, stage, stage_index, tree['jobs'])
        else:
            print("  Skipping stage: {} / {} - still in progress".format(stage_name, stage_index))


def fetch_job(pipeline_counter, pipeline_name, stage, stage_index, jobs):
    for job in jobs:
        job_name = job['name']
        agent_uuid = job['agent_uuid']
        scheduled_date = ms_timestamp_to_date(job['scheduled_date']).replace(microsecond=0)
        job_id = job['id']
        job_result = job['result']
        parser = JunitConsoleParser(pipeline_name, pipeline_counter, stage_index, stage.stage_name, job_name)
        tests_run, tests_failed, tests_skipped = parser.parse_bar_chart_info()
        job = Job(job_id, stage.stage_id, job_name, agent_uuid, scheduled_date, job_result, tests_run, tests_failed,
                  tests_skipped)
        create_job(stage, job)

        if job_result == 'Failed' and not get_connection().is_failure_downloaded(stage.stage_id):
            fetch_failure_info(stage_index, pipeline_counter, pipeline_name, stage.stage_id, stage.stage_name,
                               job_name)


def fetch_failure_info(stage_index, pipeline_counter, pipeline_name, stage_id, stage_name, job_name):
    log_parser = get_log_parser(pipeline_name)

    failure_stage = get_failure_stage(pipeline_name, pipeline_counter, stage_index, stage_name, job_name)
    get_connection().insert_failure_information(stage_id, failure_stage)

    failures = log_parser(pipeline_name, pipeline_counter, stage_index, stage_name, job_name)
    failures.insert_info(stage_id)


def ms_timestamp_to_date(ms):
    return datetime.fromtimestamp(ms / 1000.0)
