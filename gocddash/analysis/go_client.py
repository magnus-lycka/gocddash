import requests

from gocddash.util.config import PipelineConfig


class GoSource:
    def __init__(self, base_go_url, auth):
        self.base_go_url = base_go_url
        self.auth = auth

    def api_request(self, url, **kwargs):
        return self.base_request("api/" + url, **kwargs)

    def base_request(self, url, **kwargs):
        # TODO: get back the headers for agent fetching
        return requests.get(self.base_go_url + url, auth=self.auth)

    def go_request_pipeline_history(self, pipeline_name, offset=0):
        return self.api_request("pipelines/" + pipeline_name + "/history/" + str(offset))

    def go_get_pipeline_instance(self, pipeline_name, pipeline_counter):
        return self.api_request("pipelines/" + pipeline_name + "/instance/" + str(pipeline_counter) + "/").content

    def go_get_stage_instance(self, pipeline_name, pipeline_counter, stage_name):
        return self.api_request(
            "stages/" + pipeline_name + "/" + stage_name + "/instance/" + str(pipeline_counter) + "/1").content

    def go_request_stages_history(self, pipeline_name, pipeline_id, stage, stage_name):
        return self.api_request(
            "stages/" + pipeline_name + "/" + stage_name + "/instance/" + str(pipeline_id) + "/" + str(stage)).content

    def go_get_agent_information(self, agent_uuid):
        return self.api_request("agents/" + agent_uuid, headers={"Accept": "application/vnd.go.cd.v2+json"})

    def go_request_job_history(self, pipeline_name, stage_name, offset=0):
        return self.api_request(
            "jobs/" + pipeline_name + "/" + stage_name + "/defaultJob/history/" + str(offset)).content

    def go_get_pipeline_groups(self):
        return self.api_request("config/pipeline_groups").content.decode("utf-8")

    def go_request_junit_report(self, pipeline_name, pipeline_id, stage, stage_name):
        return self.base_request("files/" + pipeline_name + "/" + str(pipeline_id)
                                 + "/" + stage_name + "/" + str(
            stage) + "/defaultJob/testoutput/index.html").content.decode("utf-8")

    def go_request_console_log(self, pipeline_name, pipeline_id, stage_index, stage_name):
        return self.base_request("files/" + pipeline_name + "/" + str(pipeline_id)
                                 + "/" + stage_name + "/" + str(
            stage_index) + "/defaultJob/cruise-output/console.log").content.decode("utf-8")

    def go_request_comparison_html(self, pipeline_name, current, comparison):
        return self.base_request("compare/{}/{}/with/{}".format(pipeline_name, current, comparison)).content.decode(
            'utf-8', 'ignore')

    def go_get_cctray(self):
        return self.base_request("cctray.xml").content.decode('utf-8')


class FileSource:
    def __init__(self, directory):
        self.directory = directory

    def go_request_pipeline_history(self, pipeline_name, offset=0):
        return open(self.directory + "/history/" + pipeline_name + ".json").read()

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

    def go_get_pipeline_groups(self):
        return ""

    def go_request_console_log(self, pipeline_name, pipeline_id, stage_index, stage_name):
        return ""

    def go_request_comparison_html(self, pipeline_name, current, comparison):
        return ""

    def go_get_cctray(self):
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


def go_get_pipeline_groups():
    return source.go_get_pipeline_groups()


def go_request_junit_report(pipeline_name, pipeline_id, stage, stage_name):
    return source.go_request_junit_report(pipeline_name, pipeline_id, stage, stage_name)


def go_request_job_history(pipeline_name, stage_name, offset=0):
    return source.go_request_job_history(pipeline_name, stage_name, offset)


def go_request_console_log(pipeline_name, pipeline_id, stage_index, stage_name):
    return source.go_request_console_log(pipeline_name, pipeline_id, stage_index, stage_name)


def go_request_comparison_html(pipeline_name, current, comparison):
    return source.go_request_comparison_html(pipeline_name, current, comparison)


def go_get_cctray():
    return source.go_get_cctray()