import unittest
import requests

class CCTrayFile(object):
    def __init__(self, fn, **kwargs):
        self.xml = open(fn).read()


class CCTrayServer(object):
    def __init__(self, url, **kwargs):
        response = requests.get(url)
        assert response.status_code == 200
        self.xml = response.content


def get_cctray_source(source, **kwargs):
    if '://' in source:
        return CCTrayServer(source, **kwargs)
    else:
        return CCTrayFile(source, **kwargs)


class TestGetXML(unittest.TestCase):
    def test_fetch_xml_from_file(self):
        xml = get_cctray_source('data/cctray.xml').xml
        self.assertIn('<?xml', xml)
        self.assertIn('<Project name=', xml)

    def test_fetch_xml_from_goserver(self):
        xml = get_cctray_source('http://palanga:8153/go/cctray.xml').xml
        self.assertIn('<?xml', xml)
        self.assertIn('<Project name=', xml)


if __name__ == '__main__':
    unittest.main()
