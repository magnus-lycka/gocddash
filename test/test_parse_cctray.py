import unittest
from parse_cctray import Projects


class TestPipelines(unittest.TestCase):
    def setUp(self):
        self.projects = Projects(open('data/cctray.xml').read())
        self.pipelines = self.projects.pipelines

    def test_count_pipelines(self):
        self.assertEqual(9, len(self.projects.pipelines))

    def test_pipeline_attributes(self):
        expected = {
            "foo": ("Success", "2015-11-26T11:45:17", "http://go-server/go/pipelines/foo/382"),
            "bar": ("Failure", "2015-11-03T09:16:23", "http://go-server/go/pipelines/bar/57"),
            "baz": ("Failure", "2015-11-26T11:46:33", "http://go-server/go/pipelines/baz/203"),
            "qux": ("Building after Failure", "2015-11-26T12:29:28", "http://go-server/go/pipelines/qux/240"),
            "norf": ("Building after Success", "2015-11-26T12:10:11", "http://go-server/go/pipelines/norf/190"),
            "large-norf": ("Failure", "2015-11-20T15:44:54", "http://go-server/go/pipelines/large-norf/13"),
            "fnord": ("Success", "2015-11-26T13:15:09", "http://go-server/go/pipelines/fnord/98"),
            "snafu-service": ("Success", "2015-11-26T11:28:42", "http://go-server/go/pipelines/snafu-service/250"),
            "snafu-transformation": ("Success", "2015-11-25T14:37:04", "http://go-server/go/pipelines/snafu-transformation/100"),
        }
        for name, pipeline in self.pipelines.items():
            self.assertEqual(name, pipeline.name)
            self.assertEqual(expected[name][0], pipeline.status)
            self.assertEqual(expected[name][1], pipeline.changed)
            self.assertEqual(expected[name][2], pipeline.url)

    def test_pipeline_selection_green(self):
        expected = "fnord qux norf baz foo snafu-service snafu-transformation large-norf bar".split()
        self.assertEqual(expected, [p.name for p in self.projects.select('green')])

    def test_pipeline_selection_yellow(self):
        expected = "qux norf baz large-norf bar".split()
        self.assertEqual(expected, [p.name for p in self.projects.select('yellow')])

    def test_pipeline_selection_red(self):
        expected = "qux baz large-norf bar".split()
        self.assertEqual(expected, [p.name for p in self.projects.select('red')])


class TestStages(unittest.TestCase):
    def setUp(self):
        self.stages = Projects(open('data/cctray.xml')).pipelines['baz'].stages

    def test_pipeline_stages(self):
        self.assertEqual(2, len(self.stages))
        self.assertEqual('gamma', self.stages[0].name)
        self.assertEqual('Success', self.stages[0].status)
        self.assertEqual('http://go-server/go/pipelines/baz/203/readyToTest/1',
                         self.stages[0].url)
        self.assertEqual('delta', self.stages[1].name)
        self.assertEqual('Failure', self.stages[1].status)


class TestJobs(unittest.TestCase):
    def setUp(self):
        self.jobs = Projects(open('data/cctray.xml')).pipelines['snafu-service'].stages[1].jobs

    def test_stage_jobs(self):
        self.assertEqual(2, len(self.jobs))
        self.assertEqual('Integration_Tests', self.jobs[0].name)
        self.assertEqual('Success', self.jobs[0].status)
        self.assertEqual("http://go-server/go/tab/build/detail/snafu-service/250/test/1/Integration_Tests",
                         self.jobs[0].url)
        self.assertEqual('DB_Tests', self.jobs[1].name)
        self.assertEqual('Success', self.jobs[1].status)
        self.assertEqual("http://go-server/go/tab/build/detail/snafu-service/250/test/1/DB_Tests",
                         self.jobs[1].url)


if __name__ == '__main__':
    unittest.main()