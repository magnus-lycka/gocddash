import requests


class CCTrayFile(object):
    def __init__(self, file_name, **kwargs):
        self.cctray = open(file_name + "/cctray.xml").read()
        self.pipelinegroups = []


class CCTrayServer(object):
    def __init__(self, url, **kwargs):
        self.url = url
        self.auth = kwargs['auth']

        def fetch_from_go(path):
            response = requests.get(self.url + path, auth=self.auth)
            if response.status_code == 200:
                return response.content.decode("utf-8")
            else:
                print(response)
                raise ValueError(response.status_code)

        self.cctray = fetch_from_go('cctray.xml')
        self.pipelinegroups = fetch_from_go('api/config/pipeline_groups')


def get_cctray_source(source, **kwargs):
    if '://' in source:
        return CCTrayServer(source, **kwargs)
    else:
        return CCTrayFile(source, **kwargs)
