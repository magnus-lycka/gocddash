import unittest
from gocddash.analysis.actions import assert_correct_input


class TestAssertCorrectInput(unittest.TestCase):
    def test_assert_correct_input(self):
        pipeline_name = "hello"
        latest_pipeline = 785
        max_pipeline_in_go = 786
        subsequent_pipelines = 5
        max_available_pipeline = 785
        start = 775
        output = assert_correct_input(pipeline_name, latest_pipeline, max_pipeline_in_go,
                                      subsequent_pipelines, max_available_pipeline, start)
        self.assertEqual(output, (pipeline_name, latest_pipeline, max_pipeline_in_go,
                                  subsequent_pipelines, start))

        start = 784
        output = assert_correct_input(pipeline_name, latest_pipeline, max_pipeline_in_go,
                                      subsequent_pipelines, max_available_pipeline, start)
        self.assertEqual(output, (pipeline_name, latest_pipeline, max_pipeline_in_go, 2, start))

        latest_pipeline = 784
        max_pipeline_in_go = 785
        subsequent_pipelines = 10
        max_available_pipeline = 784
        start = 0
        with self.assertRaises(BaseException) as cm:
            assert_correct_input(pipeline_name, latest_pipeline, max_pipeline_in_go,
                                 subsequent_pipelines, max_available_pipeline, start)

            exception = cm.exception
            self.assertEqual(exception.code, 3)

if __name__ == '__main__':
    unittest.main()
