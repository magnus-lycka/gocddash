import requests


class CCTrayFile(object):
    def __init__(self, fn, **kwargs):
        self.data = open(fn).read()


class CCTrayServer(object):
    def __init__(self, url, **kwargs):
        response = requests.get(url, **kwargs)
        if response.status_code == 200:
            self.data = response.content
        else:
            print response
            raise ValueError(response.status_code)


def get_cctray_source(source, **kwargs):
    if '://' in source:
        return CCTrayServer(source, **kwargs)
    else:
        return CCTrayFile(source, **kwargs)
