#!/usr/bin/env python3

import argparse
import datetime
import os
import time
from configparser import ConfigParser
from itertools import chain

from gocddash.analysis import data_access, actions, go_request, go_client
from gocddash.dash_board import read_pipeline_config
from gocddash.util import pipeline_config


def parse_pipeline_availability(pipelines):

    available_pipelines = []
    for pipeline, begin_index in pipelines:
        if go_request.pipeline_exists_in_go(pipeline):
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


def read_cfg(path=None):
    if not path:
        path = os.getcwd() + "/gocddash/application.cfg"
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
    parser.add_argument('--db-port', help='database port, (overrides any value set in application config)')
    parser.add_argument('-p', '--pipeline-cfg', help='pipeline config')
    parser.add_argument('-f', '--file-source', help='go client file source')
    parser.add_argument('-d', '--continuous-sync', action='store_true', help='run as a daemon and continually sync pipelines')
    pargs = parser.parse_args()
    pargs_dict = vars(pargs)
    return pargs_dict


def configure_from_args(pargs_dict):
    pipeline_cfg_path = pargs_dict['pipeline_cfg']
    pipeline_config.create_pipeline_config(pipeline_cfg_path)

    app_cfg = pargs_dict['app_cfg']
    server_url, user, passwd, db_port = read_cfg(app_cfg)

    if pargs_dict['db_port']:
        db_port = pargs_dict['db_port']

    file_source = pargs_dict['file_source']
    if file_source:
        server_url = file_source

    return server_url, user, passwd, db_port


def sync_backlog(json_tree):
    requested_pipelines = read_pipeline_config.get_pipelines_to_sync(json_tree)
    log("Starting synchronization.")
    pipelines = parse_pipeline_availability(requested_pipelines)
    synchronize(pipelines)

    print("")
    log("Done with the backlog.")
    print("")
    return pipelines


def continuous_sync(pipelines):
    last_sync = datetime.datetime.now()
    while True:
        time_diff = millis_interval(last_sync, datetime.datetime.now())
        if time_diff < 2*60*1000:
            time.sleep(10)
        else:
            log("Starting synchronization.")
            last_sync = datetime.datetime.now()
            synchronize(pipelines)
            log("Synchronization finished.")


def main():
    # Instantiate config, database and go client
    pargs_dict = parse_args()

    server_url, user, passwd, db_port = configure_from_args(pargs_dict)

    data_access.create_connection(db_port)
    go_client.create_go_client(server_url, (user, passwd))

    pipelines = sync_backlog(pipeline_config.get_pipeline_config().pipelines)

    if pargs_dict["continuous_sync"]:
        continuous_sync(pipelines)


def log(string):
    print(str(datetime.datetime.now()) + " " + string)

if __name__ == '__main__':
    main()
