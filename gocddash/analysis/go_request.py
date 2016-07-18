import math
from functools import reduce

from .pipeline_fetcher import *


def calculate_request(latest_pipeline, max_pipeline_in_go, pipelines=10, start=0):
    if start == 0:
        offset = max_pipeline_in_go - latest_pipeline - pipelines
        run_times = roundup(pipelines)
        print(get_diff(latest_pipeline, latest_pipeline + pipelines, pipelines))
    else:
        offset = max_pipeline_in_go - start - pipelines + 1
        run_times = roundup(pipelines)
        print(get_diff(start, start + pipelines - 1, pipelines))

    return offset, run_times


def roundup(x):
    return int(math.ceil(x / 10.0))


def get_max_pipeline_status(pipeline_name):
    pipeline_request = go_request_pipeline_history(pipeline_name, 0)

    if pipeline_request:
        pipeline_history = json.loads(pipeline_request)
        pipelines = pipeline_history["pipelines"]

        highest_available_pipeline_index = reduce(lambda acc, pipeline: max(acc, pipeline["counter"]) if (
        pipeline["stages"][0]["result"] != "Unknown") else acc, pipelines, 0)
        return pipeline_history["pagination"]["total"], highest_available_pipeline_index
    else:
        print("Could not retrieve pipeline history from GO.")
        return 0, 0


def get_diff(from_counter, to_counter, size):
    return "Requested pipelines = " + str(size) + " (from " + str(from_counter) + " to " + str(to_counter) + ")"


def pipeline_exists_in_go(pipeline_name):
    return go_get_pipeline_status(pipeline_name) is not None
