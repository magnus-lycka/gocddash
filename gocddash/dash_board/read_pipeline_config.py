from gocddash.analysis.go_request import get_max_pipeline_status


def parse_config(json_config):
    """ Parses pipelines.json to get the pipeline name and where to start syncing from """
    name_start_tuple_list = [(key['name'], key['begin_at']) if "begin_at" in key else (
        key['name'], max(0, get_max_pipeline_status(key['name'])[1] - 20)) for key in json_config['pipelines']]

    return name_start_tuple_list


def get_pipelines_to_sync(json_config):
    return parse_config(json_config)
