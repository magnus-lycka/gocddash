import unittest

from gocddash.analysis import go_request


def get_max_mock(name):
    if name == "characterize":
        return 1800, 1800
    else:
        return 2200, 2200


class TestReadFile(unittest.TestCase):
    def testRegularConfig(self):
        input_ = dict()
        input_["pipelines"] = [
            {"name": "characterize", "begin_at": 1500},
            {"name": "feature", "begin_at": 100},
        ]

        pipelines = go_request.get_pipelines_to_sync(input_)
        self.assertEqual(pipelines, [("characterize", 1500), ("feature", 100)])

    def testNoBeginAt(self):
        saved = go_request.get_max_pipeline_status
        go_request.get_max_pipeline_status = get_max_mock

        input_ = dict()
        input_["pipelines"] = [
            {"name": "characterize", "begin_at": 1500},
            {"name": "feature"},
        ]

        pipelines = go_request.get_pipelines_to_sync(input_)
        self.assertEqual(pipelines, [("characterize", 1500), ("feature", 2180)])

        go_request.get_max_pipeline_status = saved
