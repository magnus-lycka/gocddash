import requests


class GoSource:
    def __init__(self, base_go_url, auth):
        self.base_go_url = base_go_url
        self.auth = auth

    def simple_api_request(self, url, headers=None):
        response = self.api_request(url, headers)
        if response.status_code != 200:
            raise ValueError("Got response code " + str(response.status_code) + " when requesting " + url)
        return response.content.decode("utf-8")

    def simple_request(self, url, headers=None):
        response = self.base_request(url, headers)
        if response.status_code != 200:
            raise ValueError("Got response code " + str(response.status_code) + " when requesting " + url)
        return response.content.decode("utf-8")

    def api_request(self, url, headers=None):
        return self.base_request("api/" + url, headers)

    def base_request(self, url, headers=None):
        response = requests.get(self.base_go_url + url, auth=self.auth, headers=headers)
        return response

    def go_request_pipeline_history(self, pipeline_name, offset=0):
        return self.simple_api_request("pipelines/" + pipeline_name + "/history/" + str(offset))

    def go_get_pipeline_instance(self, pipeline_name, pipeline_counter):
        return self.simple_api_request("pipelines/" + pipeline_name + "/instance/" + str(pipeline_counter) + "/")

    def go_get_pipeline_status(self, pipeline_name):
        return self.simple_api_request("pipelines/" + pipeline_name + "/status")

    def go_get_stage_instance(self, pipeline_name, pipeline_counter, stage_name):
        return self.simple_api_request(
            "stages/" + pipeline_name + "/" + stage_name + "/instance/" + str(pipeline_counter) + "/1")

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

    def go_request_junit_report(self, pipeline_name, pipeline_id, stage, stage_name):
        return self.simple_request("files/" + pipeline_name + "/" + str(pipeline_id)
                                 + "/" + stage_name + "/" + str(
            stage) + "/defaultJob/testoutput/index.html")

    def go_request_console_log(self, pipeline_name, pipeline_id, stage_index, stage_name):
        return self.simple_request("files/" + pipeline_name + "/" + str(pipeline_id)
                                 + "/" + stage_name + "/" + str(
            stage_index) + "/defaultJob/cruise-output/console.log")

    def go_request_comparison_html(self, pipeline_name, current, comparison):
        return self.simple_request("compare/{}/{}/with/{}".format(pipeline_name, current, comparison))

    def go_get_cctray(self):
        return self.simple_request("cctray.xml")


class FileSource:
    def __init__(self, directory):
        self.directory = directory

    def read_file(self, path):
        return open(self.directory + path).read()

    def go_request_pipeline_history(self, pipeline_name, offset=0):
        return self.read_file("/history/" + pipeline_name + ".json")

    def go_get_pipeline_instance(self, pipeline_name, pipeline_counter):
        return ""

    def go_get_pipeline_status(self, pipeline_name):
        return self.read_file("/status/" + pipeline_name + ".json")

    def go_get_stage_instance(self, pipeline_name, pipeline_counter, stage_name):
        return ""

    def go_request_stages_history(self, pipeline_name, pipeline_counter, stage_index, stage_name):
        return self.read_file("/stages/" + pipeline_name + "_" + str(pipeline_counter) + "_" + stage_name + "_" + str(stage_index) + ".json")

    def go_get_agent_information(self, agent_uuid):
        return True, self.read_file("/agents/" + agent_uuid + ".json")

    def go_request_junit_report(self, pipeline_name, pipeline_id, stage, stage_name):
        return ""

    def go_request_job_history(self, pipeline_name, stage_name, offset=0):
        return ""

    def go_get_pipeline_groups(self):
        return self.read_file("/config/pipeline_groups.json")

    def go_request_console_log(self, pipeline_name, pipeline_id, stage_index, stage_name):
        return ""

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


def go_request_stages_history(pipeline_name, pipeline_counter, stage_index, stage_name):
    return _go_client.go_request_stages_history(pipeline_name, pipeline_counter, stage_index, stage_name)


def go_get_agent_information(agent_uuid):
    return _go_client.go_get_agent_information(agent_uuid)


def go_get_pipeline_groups():
    return _go_client.go_get_pipeline_groups()


def go_request_junit_report(pipeline_name, pipeline_id, stage, stage_name):
    return _go_client.go_request_junit_report(pipeline_name, pipeline_id, stage, stage_name)


def go_request_job_history(pipeline_name, stage_name, offset=0):
    return _go_client.go_request_job_history(pipeline_name, stage_name, offset)


def go_request_console_log(pipeline_name, pipeline_id, stage_index, stage_name):
    return _go_client.go_request_console_log(pipeline_name, pipeline_id, stage_index, stage_name)


def go_request_comparison_html(pipeline_name, current, comparison):
    return _go_client.go_request_comparison_html(pipeline_name, current, comparison)


def go_get_cctray():
    return _go_client.go_get_cctray()


_go_client = None


def create_go_client(base_go_url, auth):
    global _go_client
    if "http" in base_go_url:
        _go_client = GoSource(base_go_url, auth)
    else:
        _go_client = FileSource(base_go_url)
    return _go_client


def get_client():
    if not _go_client:
        raise ValueError("GO client not instantiated")
    return _go_client
