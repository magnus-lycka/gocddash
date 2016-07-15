import unittest
from gocddash.analysis.go_request import calculate_request


class TestGoFailureExtractor(unittest.TestCase):
    def test_no_start_specified(self):
        offset, run_times = calculate_request(1900, 1910, pipelines=10)
        self.assertEqual(offset, 0)
        self.assertEqual(run_times, 1)

    def test_go_request_request(self):
        offset, run_times = calculate_request(750, 785, start=750, pipelines=25)
        self.assertEqual(offset, 11)
        self.assertEqual(run_times, 3)

        offset, run_times = calculate_request(745, 772, start=750)
        self.assertEqual(offset, 13)
        self.assertEqual(run_times, 1)

        offset, run_times = calculate_request(772, 772, 1000)
        self.assertEqual(offset, -1000)
        self.assertEqual(run_times, 100)

    def test_sync_latest(self):
        offset, run_times = calculate_request(2017, 2018, 1, 2017)
        self.assertEqual(offset, 1)
        self.assertEqual(run_times, 1)

    def test_at_latest_already(self):
        offset, run_times = calculate_request(883, 883, 0, 0)
        self.assertEqual(offset, 0)
        self.assertEqual(run_times, 0)

    def test_pull_max(self):
        offset, run_times = calculate_request(0, 2096, pipelines=2096-2050, start=2050)
        self.assertEqual(offset, 1)
        self.assertEqual(run_times, 5)

if __name__ == '__main__':
    unittest.main()
