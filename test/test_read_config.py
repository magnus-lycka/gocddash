import unittest

from gocddash.dashboard import read_pipeline_config


def get_max_mock(name):
    if name == "characterize":
        return 1800, 1800
    else:
        return 2200, 2200


class TestReadFile(unittest.TestCase):
    def testRegularConfig(self):
        input = dict()
        input["pipelines"] = [
            {"name": "characterize", "begin_at": 1500},
            {"name": "feature", "begin_at": 100},
        ]

        pipelines = read_pipeline_config.get_pipelines_to_sync(input)
        self.assertEqual(pipelines, [("characterize", 1500), ("feature", 100)])

    def testNoBeginAt(self):
        saved = read_pipeline_config.get_max_pipeline_status
        read_pipeline_config.get_max_pipeline_status = get_max_mock

        input = dict()
        input["pipelines"] = [
            {"name": "characterize", "begin_at": 1500},
            {"name": "feature"},
        ]

        pipelines = read_pipeline_config.get_pipelines_to_sync(input)
        self.assertEqual(pipelines, [("characterize", 1500), ("feature", 2180)])

        read_pipeline_config.get_max_pipeline_status = saved
