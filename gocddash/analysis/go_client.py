import requests

from gocddash.util.config import PipelineConfig


class GoSource:
    def __init__(self, base_go_url, auth):
        self.base_go_url = base_go_url
        self.api_go_url = base_go_url + "api/"
        self.auth = auth
    
    def go_request_pipeline_history(self, pipeline_name, offset=0):
        request = requests.get(self.api_go_url + "pipelines/" + pipeline_name + "/history/" + str(offset), auth=self.auth)
        return request

    def go_get_pipeline_instance(self, pipeline_name, pipeline_counter):
        return requests.get(self.api_go_url + "pipelines/" + pipeline_name + "/instance/" + str(pipeline_counter) + "/",
                            auth=self.auth).content

    def go_get_stage_instance(self, pipeline_name, pipeline_counter, stage_name):
        return requests.get(
            self.api_go_url + "stages/" + pipeline_name + "/" + stage_name + "/instance/" + str(pipeline_counter) + "/1",
            auth=self.auth).content

    def go_request_stages_history(self, pipeline_name, pipeline_id, stage, stage_name):
        return requests.get(
            self.api_go_url + "stages/" + pipeline_name + "/" + stage_name + "/instance/" + str(pipeline_id) + "/" + str(
                stage),
            auth=self.auth).content

    def go_get_agent_information(self, agent_uuid):
        return requests.get(self.api_go_url + "agents/" + agent_uuid, auth=self.auth,
                            headers={"Accept": "application/vnd.go.cd.v2+json"})

    def go_request_junit_report(self, pipeline_name, pipeline_id, stage, stage_name):
        return requests.get(self.base_go_url + "files/" + pipeline_name + "/" + str(pipeline_id)
                            + "/" + stage_name + "/" + str(stage) + "/defaultJob/testoutput/index.html",
                            auth=self.auth).content.decode("utf-8")

    def go_request_job_history(self, pipeline_name, stage_name, offset=0):
        return requests.get(
            self.api_go_url + "jobs/" + pipeline_name + "/" + stage_name + "/defaultJob/history/" + str(offset),
            auth=self.auth).content

    def go_request_console_log(self, pipeline_name, pipeline_id, stage_index, stage_name):
        return requests.get(self.base_go_url + "files/" + pipeline_name + "/" + str(pipeline_id)
                            + "/" + stage_name + "/" + str(stage_index) + "/defaultJob/cruise-output/console.log",
                            auth=self.auth).content.decode("utf-8")

    def go_request_comparison_html(self, pipeline_name, current, comparison):
        return requests.get(self.base_go_url + "compare/{}/{}/with/{}".format(pipeline_name, current, comparison),
                            auth=self.auth).content.decode('utf-8', 'ignore')

class FileSource:
    def go_request_pipeline_history(self, pipeline_name, offset=0):
        return ""

    def go_get_pipeline_instance(self, pipeline_name, pipeline_counter):
        return ""

    def go_get_stage_instance(self, pipeline_name, pipeline_counter, stage_name):
        return ""

    def go_request_stages_history(self, pipeline_name, pipeline_id, stage, stage_name):
        return ""

    def go_get_agent_information(self, agent_uuid):
        return ""

    def go_request_junit_report(self, pipeline_name, pipeline_id, stage, stage_name):
        return ""

    def go_request_job_history(self, pipeline_name, stage_name, offset=0):
        return ""

    def go_request_console_log(self, pipeline_name, pipeline_id, stage_index, stage_name):
        return ""

    def go_request_comparison_html(self, pipeline_name, current, comparison):
        return ""


source = GoSource(PipelineConfig().get_base_go_url(), PipelineConfig().get_auth())


def go_request_pipeline_history(pipeline_name, offset=0):
    return source.go_request_pipeline_history(pipeline_name, offset)


def go_get_pipeline_instance(pipeline_name, pipeline_counter):
    return source.go_get_pipeline_instance(pipeline_name, pipeline_counter)


def go_get_stage_instance(pipeline_name, pipeline_counter, stage_name):
    return source.go_get_stage_instance(pipeline_name, pipeline_counter, stage_name)


def go_request_stages_history(pipeline_name, pipeline_id, stage, stage_name):
    return source.go_request_stages_history(pipeline_name, pipeline_id, stage, stage_name)


def go_get_agent_information(agent_uuid):
    return source.go_get_agent_information(agent_uuid)


def go_request_junit_report(pipeline_name, pipeline_id, stage, stage_name):
    return source.go_request_junit_report(pipeline_name, pipeline_id, stage, stage_name)


def go_request_job_history(pipeline_name, stage_name, offset=0):
    return source.go_request_job_history(pipeline_name, stage_name, offset)


def go_request_console_log(pipeline_name, pipeline_id, stage_index, stage_name):
    return source.go_request_console_log(pipeline_name, pipeline_id, stage_index, stage_name)


def go_request_comparison_html(pipeline_name, current, comparison):
    return source.go_request_comparison_html(pipeline_name, current, comparison)