import unittest
from parse_cctray import Projects


class TestParseProjects(unittest.TestCase):
    def setUp(self):
        self.projects = Projects('data/cctray.xml')

    def test_count_projects(self):
        self.assertEqual(len(self.projects.tree.findall('Project')), 23)

    def test_activity_count(self):
        activities = {
            'Sleeping': 19,
            'Building': 4,
        }
        for activity_type, count in activities.items():
            self.assertEqual(len(self.projects.activities[activity_type]), count)

    def test_count_pipelines(self):
        self.assertEqual(len(self.projects.pipelines), 9)

    def test_count_stages(self):
        self.assertEqual(len(self.projects.stages['snafu-service']), 2)

    def test_count_jobs(self):
        self.assertEqual(len(self.projects.jobs[('snafu-service', 'test')]), 2)

    def test_pipeline_staus(self):
        expected = {
            "foo": "Success",
            "bar": "Failure",
            "baz": "Failure",
            "qux": "Building after Failure",
            "norf": "Building after Success",
            "large-norf": "Failure",
            "fnord": "Success",
            "snafu-service": "Success",
            "snafu-transformation": "Success",
        }
        for name, pipeline in self.projects.pipelines.items():
            self.assertEqual(pipeline.status, expected[name])


if __name__ == '__main__':
    unittest.main()