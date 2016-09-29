"""Most of the methods in this file are old development for the characterize specific ML algorithms"""
import collections
import re

from .data_access import get_connection


def filter_docnames(pipeline_name):
    document_names = get_connection().get_texttest_document_names(pipeline_name)
    filtered_document_names = document_filter(document_names)
    return filtered_document_names


def document_filter(document_names):
    return list(map(lambda s: document_name_split(s) if s else "", document_names))


def document_name_split(name):
    return name[:re.search(
        "(catalogue|routingLog|eventsLog|performance|stderr|stdout|"
        "exitcode|documentMetadata|internalxml|primarypres|target)",
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
    return failure_information


def construct_failure_signature(stage_id, test_map):
    """ Old characterize specific ML method """
    signature = ""
    for test_index, document_list in test_map.items():
        signature += str(test_index)
        for document in document_list:
            signature += document[0][0] + document[1] + "|"
    return stage_id, signature


def create_binary_test_index_list(failure_indices):
    """ Old characterize specific ML method """
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
    """ Old characterize specific ML method """
    consecutive_binary_list = []
    sorted_failure_indices = sorted(failure_indices.items())
    # PyCharm inspection bug, https://youtrack.jetbrains.com/issue/PY-17759
    # noinspection PyArgumentList
    od = collections.OrderedDict(sorted_failure_indices)
    for index, value in enumerate(od.items()):
        if value[1] == od.values()[index - 1]:
            consecutive_binary_list.append((value[0], 1))
        else:
            consecutive_binary_list.append((value[0], 0))
    return consecutive_binary_list
