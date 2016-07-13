#!/usr/bin/env python3

import codecs
import datetime
import json
import time

from analysis import data_access, actions, go_request
from dash_board.read_config import *


def parse_pipeline_availability(pipelines):
    synced_pipelines = data_access.get_synced_pipelines()
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
        synced_pipeline_counter = data_access.get_highest_pipeline_count(pipeline)
        sync_begin_index = max(begin_sync_index, synced_pipeline_counter)
        max_in_go = get_max_pipeline_status(pipeline)[1]
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


def main():
    with codecs.open("pipelines.json", encoding='utf-8') as input_reader: # TODO: does this mean that this is open through the entire lifecycle?
        json_tree = json.load(input_reader)
        requested_pipelines = get_pipelines_to_sync(json_tree)
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