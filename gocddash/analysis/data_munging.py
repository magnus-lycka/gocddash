import collections
import re

from gocddash.util.file_storage import read_data
from .data_access import get_connection


def filter_docnames(pipeline_name):
    document_names = get_connection().get_texttest_document_names(pipeline_name)
    filtered_document_names = document_filter(document_names)
    return filtered_document_names


def document_filter(document_names):
    return list(map(lambda s: document_name_split(s) if s else "", document_names))


def document_name_split(name):
    return name[:re.search(
        "(catalogue|routingLog|eventsLog|performance|stderr|stdout|exitcode|documentMetadata|internalxml|primarypres|target)",
        name).end()]


def texttest_failure_group_by_stage(rows):
    stage_map = {}
    for row in rows:
        test_map = stage_map.get(row[1], {})
        index_list = test_map.get(row[2], [])
        index_list.append((row[3], document_name_split(row[4])))
        test_map[row[2]] = index_list
        stage_map[row[1]] = test_map
    return stage_map


def binary_dependent_variable(result_column):
    return map(lambda s: 0 if s == "Failed" else 1, result_column)


def get_failure_stage_signature(stage_id):
    return texttest_failure_group_by_stage(get_connection().get_stage_texttest_failures(stage_id))


def get_failure_signatures(pipeline_name):
    failure_information = texttest_failure_group_by_stage(get_connection().get_texttest_failures(pipeline_name))
    failure_signatures = []
    # print failure_information

    # for stage_id, test_map in failure_information.items():
    #     failure_signatures.append(construct_failure_signature(stage_id, test_map))

    return failure_information


def construct_failure_signature(stage_id, test_map):
    signature = ""
    for test_index, document_list in test_map.items():
        signature += str(test_index)
        for document in document_list:
            signature += document[0][0] + document[1] + "|"
    return stage_id, signature


def create_binary_test_index_list(failure_indices):
    id_index_pair = []
    for key, value in failure_indices.items():
        zero_list = [0 for _ in range(13)]
        for index in value.keys():
            zero_list[index - 1] = 1
        zero_list.insert(0, key)
        row_content = list(zip(*zip(zero_list)))[0]
        id_index_pair.append(row_content)
    return id_index_pair


def check_if_consecutive_failure_signature(failure_indices):
    consecutive_binary_list = []
    od = collections.OrderedDict(sorted(failure_indices.items()))
    for index, value in enumerate(od.items()):
        if value[1] == od.values()[index - 1]:
            consecutive_binary_list.append((value[0], 1))
        else:
            consecutive_binary_list.append((value[0], 0))
    return consecutive_binary_list


def export_data_to_pandas_df(pipeline_name):
    """ Exports the desired pipeline data from the postgresql database and returns a pandas dataframe """

    collated_data = read_data(get_connection().get_failure_statistics(pipeline_name),
                              ["Pipelinename", "counter", "trigger_message", "approved_by", "stageindex",
                               "scheduleddate",
                               "agent_name", "failure_stage", "result", "id", "stagename"])
    binary_result_column = binary_dependent_variable(collated_data.result)
    collated_data.result = binary_result_column

    return collated_data
