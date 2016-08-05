#!/usr/bin/env python3

import argparse
import codecs
import datetime
import json
import os
import time
from configparser import ConfigParser
from itertools import chain

from gocddash.analysis import data_access, actions, go_request, go_client, domain
from gocddash.dash_board import read_config
from gocddash.util import config


def parse_pipeline_availability(pipelines):
    synced_pipelines = list(map(lambda phs: (phs.pipeline_name, phs.pipeline_counter), domain.get_pipeline_heads()))
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
        max_in_go = go_request.get_max_pipeline_status(pipeline)[0]
        number_of_pipelines = max_in_go - sync_begin_index
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
    return map(lambda s: cfg[s].strip('"'), ['go_server_url', 'go_server_user', 'go_server_passwd', 'db_port'])


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--app-cfg', help='application config')
    parser.add_argument('-p', '--pipeline-cfg', help='pipeline config')
    parser.add_argument('-f', '--file-source', help='go client file source')
    pargs = parser.parse_args()
    pargs_dict = vars(pargs)
    return pargs_dict


def main():
    # Instantiate config, database and go client
    pargs_dict = parse_args()

    pipeline_cfg = pargs_dict['pipeline_cfg']
    if pipeline_cfg:
        config.create_pipeline_config(pipeline_cfg)
    else:
        config.create_pipeline_config()
    pipelines_path = config.get_config().path

    app_cfg = pargs_dict['app_cfg']
    if app_cfg:
        server_url, user, passwd, db_port = read_cfg(app_cfg)
    else:
        server_url, user, passwd, db_port = read_cfg()

    file_source = pargs_dict['file_source']
    if file_source:
        server_url = file_source

    data_access.create_connection(db_port)
    go_client.create_go_client(server_url, (user, passwd))

    with codecs.open(pipelines_path, encoding='utf-8') as input_reader:
        json_tree = json.load(input_reader)
        requested_pipelines = read_config.get_pipelines_to_sync(json_tree)
        log("Starting synchronization.")
        pipelines = parse_pipeline_availability(requested_pipelines)
        synchronize(pipelines)

        print("")
        log("Done with the backlog.")
        print("")

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