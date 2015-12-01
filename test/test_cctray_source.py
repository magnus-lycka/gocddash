import unittest

from cctray_source import get_cctray_source


class TestGetXML(unittest.TestCase):
    def test_fetch_xml_from_file(self):
        xml = get_cctray_source('data/cctray.xml').xml
        self.assertIn('<?xml', xml)
        self.assertIn('<Project name=', xml)

    def test_fetch_xml_from_goserver(self):
        xml = get_cctray_source('http://go.pagero.local/go/cctray.xml').xml
        self.assertIn('<?xml', xml)
        self.assertIn('<Project name=', xml)


if __name__ == '__main__':
    unittest.main()
