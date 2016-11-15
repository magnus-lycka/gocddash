"""
Most of the methods in this file are old development for the characterize specific ML algorithms
"""
import re

from .data_access import get_connection


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


def get_failure_stage_signature(stage_id):
    return texttest_failure_group_by_stage(get_connection().get_stage_texttest_failures(stage_id))
