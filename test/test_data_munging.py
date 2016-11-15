import unittest

from gocddash.analysis.characterize_data_munging import texttest_failure_group_by_stage

document_names = ['catalogue', 'documentMetadata1782638714687', 'eventsLog', 'exitcode', 'internalxml_OR-1782638714687',
                  'primarypres1782638714687', 'routingLog', 'stderr', 'catalogue', 'documentMetadata1782638714687',
                  'eventsLog', 'exitcode', 'internalxml_OR-1782638714687', 'primarypres1782638714687', 'routingLog',
                  'stderr']


class TestFileStorage(unittest.TestCase):
    def test_group_by(self):
        db_rows = [
            (1, 34578, 12, "missing", "target"),
            (2, 34578, 2, "new", "documentMetadata1782638714687"),
            (3, 34578, 2, "new", "internalxml")
        ]
        output = texttest_failure_group_by_stage(db_rows)
        self.assertEqual(output, {
            34578: {2: [("new", "documentMetadata"), ("new", "internalxml")], 12: [("missing", "target")]}})


if __name__ == '__main__':
    unittest.main()
