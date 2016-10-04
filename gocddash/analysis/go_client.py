import requests
from urllib.parse import quote
from werkzeug.contrib.cache import SimpleCache, MemcachedCache

cache_timeout = 10
try:
    cache = MemcachedCache(default_timeout=cache_timeout)
    print("Started MemchachedCache")
    # Provoke failure unless the service is running.
    cache.get('X')
except Exception as error:
    cache = SimpleCache(default_timeout=cache_timeout)
    print('Fell back on SimpleCache due to', error)


class GoSource:  # pragma: no cover
    """
    Performs REST API requests to Go-server
    """
    def __init__(self, base_go_url, auth):
        self.base_go_url = base_go_url
        self.auth = auth
        self.consecutive_cache_errors = 0

    def simple_api_request(self, url, headers=None):
        response = self.api_request(url, headers)
        return self.unwrap_response(response)

    def simple_request(self, url, headers=None):
        response = self.base_request(url, headers)
        return self.unwrap_response(response)

    @staticmethod
    def unwrap_response(response):
        if response.status_code != 200:
            raise ValueError("Got response code {} when requesting {}".format(response.status_code, response.url))
        return response.content.decode("utf-8")

    def api_request(self, url, headers=None):
        return self.base_request("api/" + url, headers)

    def base_request(self, url, headers=None):
        try:
            response = cache.get('url={};headers={}'.format(url, quote(repr(headers))))
            self.consecutive_cache_errors = 0
            if response is not None:
                return response
        except Exception as cache_error:
            self.cache_failure()
            print(cache_error)
            print('Failed to get cache for url={};headers={}'.format(url, quote(repr(headers))))
        response = requests.get(self.base_go_url + url, auth=self.auth, headers=headers)
        try:
            ok = cache.set('url=%s;headers=%s' % (url, quote(repr(headers))), response)
            if ok:
                self.consecutive_cache_errors = 0
            else:
                raise RuntimeError('cache.set() failed')
        except Exception as cache_error:
            self.cache_failure()
            print(cache_error)
            print('Failed to cache url={};headers={}'.format(url, quote(repr(headers))))
            print('Value:', response)
        return response

    def cache_failure(self):
        max_fails = 10
        self.consecutive_cache_errors += 1
        if self.consecutive_cache_errors >= max_fails:
            global cache
            cache = SimpleCache(default_timeout=cache_timeout)
            print('Fell back on SimpleCache due to {} consecutive cache failures.'.format(max_fails))

    def go_request_pipeline_history(self, pipeline_name, offset=0):
        return self.simple_api_request("pipelines/{}/history/{}".format(pipeline_name, offset))

    def go_get_pipeline_instance(self, pipeline_name, pipeline_counter):
        return self.simple_api_request("pipelines/{}/instance/{}/".format(pipeline_name, pipeline_counter))

    def go_get_pipeline_status(self, pipeline_name):
        response = self.api_request("pipelines/{}/status".format(pipeline_name))
        return response.content.decode("utf-8")

    def go_get_stage_instance(self, pipeline_name, pipeline_counter, stage_name):
        template = "stages/{}/{}/instance/{}/1"
        return self.simple_api_request(template.format(pipeline_name, stage_name, pipeline_counter))

    def go_request_stages_history(self, pipeline_name, pipeline_id, stage, stage_name):
        return self.simple_api_request(
            "stages/" + pipeline_name + "/" + stage_name + "/instance/" + str(pipeline_id) + "/" + str(stage))

    def go_get_agent_information(self, agent_uuid):
        request = self.api_request("agents/" + agent_uuid, headers={"Accept": "application/vnd.go.cd.v2+json"})
        return request.status_code == 200, request.content.decode("utf-8")

    def go_request_job_history(self, pipeline_name, stage_name, offset=0):
        return self.simple_api_request(
            "jobs/" + pipeline_name + "/" + stage_name + "/defaultJob/history/" + str(offset))

    def go_get_pipeline_groups(self):
        return self.simple_api_request("config/pipeline_groups")

    def go_request_junit_report(self, pipeline_name, pipeline_id, stage, stage_name, job_name):
        template = "files/{}/{}/{}/{}/{}/testoutput/index.html"
        request = self.base_request(template.format(pipeline_name, pipeline_id, stage_name, stage, job_name))
        return request.status_code == 200, request.content.decode("utf-8")

    def go_request_console_log(self, pipeline_name, pipeline_id, stage_index, stage_name, job_name):
        template = "files/{}/{}/{}/{}/{}/cruise-output/console.log"
        return self.simple_request(template.format(pipeline_name, pipeline_id, stage_name, stage_index, job_name))

    def go_request_comparison_html(self, pipeline_name, current, comparison):
        return self.simple_request("compare/{}/{}/with/{}".format(pipeline_name, current, comparison))

    def go_get_cctray(self):
        return self.simple_request("cctray.xml")


# noinspection PyUnusedLocal
class FileSource:
    """
    Mock version of the GoSource class.
    Routes all requests to files instead of the GO API.

    Used for testing.
    """

    def __init__(self, directory):
        self.directory = directory

    def read_file(self, path):
        return open(self.directory + path).read()

    def go_request_pipeline_history(self, pipeline_name, offset=0):
        return self.read_file("/history/" + pipeline_name + ".json")

    @staticmethod
    def go_get_pipeline_instance(pipeline_name, pipeline_counter):
        raise NotImplementedError

    def go_get_pipeline_status(self, pipeline_name):
        return self.read_file("/status/" + pipeline_name + ".json")

    @staticmethod
    def go_get_stage_instance(pipeline_name, pipeline_counter, stage_name):
        raise NotImplementedError

    def go_request_stages_history(self, pipeline_name, pipeline_counter, stage_index, stage_name):
        return self.read_file("/stages/" + pipeline_name + "_" + str(pipeline_counter) + "_" + stage_name + "_" + str(
            stage_index) + ".json")

    def go_get_agent_information(self, agent_uuid):
        return True, self.read_file("/agents/" + agent_uuid + ".json")

    def go_request_junit_report(self, pipeline_name, pipeline_counter, stage_counter, stage_name, job_name):
        if job_name == "404Job":
            return False, ''
        if job_name == "noTestsJob":
            return True, self.read_file("/junit_no_tests.html")
        if job_name == "specialJob":
            return True, self.read_file("/junit_passed.html")
        return True, self.read_file("/junit.html")

    @staticmethod
    def go_request_job_history(pipeline_name, stage_name, offset=0):
        raise NotImplementedError

    def go_get_pipeline_groups(self):
        return self.read_file("/config/pipeline_groups.json")

    def go_request_console_log(self, pipeline_name, pipeline_id, stage_index, stage_name, job_name):
        return self.read_file("/console.log")

    def go_request_comparison_html(self, pipeline_name, current, comparison):
        return self.read_file("/compare.html")

    def go_get_cctray(self):
        return self.read_file("/config/cctray.xml")


def go_request_pipeline_history(pipeline_name, offset=0):
    return _go_client.go_request_pipeline_history(pipeline_name, offset)


def go_get_pipeline_instance(pipeline_name, pipeline_counter):
    return _go_client.go_get_pipeline_instance(pipeline_name, pipeline_counter)


def go_get_stage_instance(pipeline_name, pipeline_counter, stage_name):
    return _go_client.go_get_stage_instance(pipeline_name, pipeline_counter, stage_name)


def go_get_pipeline_status(pipeline_name):
    return _go_client.go_get_pipeline_status(pipeline_name)


def go_request_stage_instance(pipeline_name, pipeline_counter, stage_index, stage_name):
    return _go_client.go_request_stages_history(pipeline_name, pipeline_counter, stage_index, stage_name)


def go_get_agent_information(agent_uuid):
    return _go_client.go_get_agent_information(agent_uuid)


def go_get_pipeline_groups():
    return _go_client.go_get_pipeline_groups()


def go_request_junit_report(pipeline_name, pipeline_id, stage, stage_name, job_name):
    return _go_client.go_request_junit_report(pipeline_name, pipeline_id, stage, stage_name, job_name)


def go_request_job_history(pipeline_name, stage_name, offset=0):
    return _go_client.go_request_job_history(pipeline_name, stage_name, offset)


def go_request_console_log(pipeline_name, pipeline_id, stage_index, stage_name, job_name):
    return _go_client.go_request_console_log(pipeline_name, pipeline_id, stage_index, stage_name, job_name)


def go_request_comparison_html(pipeline_name, current, comparison):
    return _go_client.go_request_comparison_html(pipeline_name, current, comparison)


def go_get_cctray():
    return _go_client.go_get_cctray()


_go_client = None


def create_go_client(base_go_url, auth):
    global _go_client
    if "http" in base_go_url:  # pragma: no cover
        _go_client = GoSource(base_go_url, auth)
    else:
        _go_client = FileSource(base_go_url)
    return _go_client
