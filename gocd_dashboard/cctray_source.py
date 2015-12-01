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
