#!/usr/bin/env python3

import codecs
import datetime
import json
import time
from configparser import ConfigParser
from itertools import chain
import os
import argparse

from gocddash.analysis import data_access, actions, go_request, go_client
from gocddash.dash_board import read_config
from gocddash.util import config


def parse_pipeline_availability(pipelines):
    synced_pipelines = data_access.get_connection().get_synced_pipelines()
    local_pipelines, local_pipeline_counters = zip(*synced_pipelines) if synced_pipelines else ([], [])

    available_pipelines = []
    for pipeline, begin_index in pipelines:
        if pipeline in local_pipelines or go_request.pipeline_exists_in_go(pipeline):
            available_pipelines.append((pipeline, begin_index))
        else:
            log("Pipeline " + pipeline + " is not available. This pipeline will be skipped.")

    return available_pipelines


def synchronize(pipelines):
    for pipeline, begin_sync_index in pipelines:
        synced_pipeline_counter = data_access.get_connection().get_highest_pipeline_count(pipeline)
        sync_begin_index = max(begin_sync_index, synced_pipeline_counter)
        max_in_go = go_request.get_max_pipeline_status(pipeline)[1]
        number_of_pipelines = max_in_go - sync_begin_index  # This becomes -1 when syncing a currently building re-run ?
        log("Will synchronize " + pipeline + " from " + str(sync_begin_index) + " onwards.")

        if sync_begin_index == max_in_go:
            actions.fetch_pipelines(pipeline, sync_begin_index, max_in_go, 10, 0)
        else:
            actions.fetch_pipelines(pipeline, sync_begin_index, max_in_go, number_of_pipelines, 0)


def millis_interval(start, end):
    diff = end - start
    millis = diff.days * 24 * 60 * 60 * 1000
    millis += diff.seconds * 1000
    millis += diff.microseconds / 1000
    return millis


def read_cfg(path=os.getcwd() + "/gocddash/application.cfg"):
    parser = ConfigParser()
    if not os.path.exists(path):
        raise FileNotFoundError("Error: Missing application.cfg file in {}".format(path))
    with open(path) as lines:
        lines = chain(("[top]",), lines)  # Reads cfg file without section headers
        parser.read_file(lines)
    cfg = dict(parser.items('top'))
    return cfg['go_server_url'].strip('"'), cfg['go_server_user'].strip('"'), cfg['go_server_passwd'].strip('"')


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--app-cfg', help='application config')
    parser.add_argument('-p', '--pipeline-cfg', help='pipeline config')
    pargs = parser.parse_args()
    pargs_dict = vars(pargs)
    return pargs_dict


def main():
    # Instantiate config, database and go client
    data_access.create_connection()
    pargs_dict = parse_args()

    pipeline_cfg = pargs_dict['pipeline_cfg']
    if pipeline_cfg:
        config.create_pipeline_config(pipeline_cfg)
    else:
        config.create_pipeline_config()
    pipelines_path = config.get_config().path

    app_cfg = pargs_dict['app_cfg']
    if app_cfg:
        server_url, user, passwd = read_cfg(app_cfg)
    else:
        server_url, user, passwd = read_cfg()

    go_client.create_go_client(server_url, (user, passwd))

    with codecs.open(pipelines_path, encoding='utf-8') as input_reader: # TODO: does this mean that this is open through the entire lifecycle?
        json_tree = json.load(input_reader)
        requested_pipelines = read_config.get_pipelines_to_sync(json_tree)
        log("Starting synchronization.")
        pipelines = parse_pipeline_availability(requested_pipelines)
        synchronize(pipelines)

        print()
        log("Done with the backlog.")
        print()

        last_sync = datetime.datetime.now()
        while True:
            time_diff = millis_interval(last_sync, datetime.datetime.now())
            if time_diff < 5*60*1000:
                time.sleep(10)
            else:
                log("Starting synchronization.")
                last_sync = datetime.datetime.now()
                synchronize(pipelines)
                log("Synchronization finished.")


def log(string):
    print(str(datetime.datetime.now()) + " " + string)

if __name__ == '__main__':
    main()