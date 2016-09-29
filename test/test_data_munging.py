import unittest

from gocddash.analysis.characterize_data_munging import document_filter, texttest_failure_group_by_stage, \
    create_binary_test_index_list

document_names = ['catalogue', 'documentMetadata1782638714687', 'eventsLog', 'exitcode', 'internalxml_OR-1782638714687',
                  'primarypres1782638714687', 'routingLog', 'stderr', 'catalogue', 'documentMetadata1782638714687',
                  'eventsLog', 'exitcode', 'internalxml_OR-1782638714687', 'primarypres1782638714687', 'routingLog',
                  'stderr']


class TestFileStorage(unittest.TestCase):
    def test_document_filtering(self):
        output = document_filter(document_names)
        self.assertEqual(output,
                         ["catalogue", "documentMetadata", 'eventsLog', 'exitcode', 'internalxml', 'primarypres',
                          'routingLog', 'stderr', 'catalogue', 'documentMetadata', 'eventsLog', 'exitcode',
                          'internalxml', 'primarypres', 'routingLog', "stderr"])

    def test_group_by(self):
        db_rows = [
            (1, 34578, 12, "missing", "target"),
            (2, 34578, 2, "new", "documentMetadata1782638714687"),
            (3, 34578, 2, "new", "internalxml")
        ]
        output = texttest_failure_group_by_stage(db_rows)
        self.assertEqual(output, {
            34578: {2: [("new", "documentMetadata"), ("new", "internalxml")], 12: [("missing", "target")]}})

    def test_console_fetcher_parse_test_index(self):
        input_ = {34578: {2: [("new", "documentMetadata"), ("new", "internalxml")], 12: [("missing", "target")]}}
        output = create_binary_test_index_list(input_)
        self.assertEqual(output, [(34578, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0)])


if __name__ == '__main__':
    unittest.main()
