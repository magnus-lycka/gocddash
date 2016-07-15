import requests

from util.config import PipelineConfig

base_go_url = PipelineConfig().get_base_go_url()
api_go_url = PipelineConfig().get_base_go_url() + "api/"
auth = PipelineConfig().get_auth()


def go_request_pipeline_history(pipeline_name, offset=0):
    request = requests.get(api_go_url + "pipelines/" + pipeline_name + "/history/" + str(offset), auth=auth)
    return request


def go_get_pipeline_instance(pipeline_name, pipeline_counter):
    return requests.get(api_go_url + "pipelines/" + pipeline_name + "/instance/" + str(pipeline_counter) + "/",
                        auth=auth).content


def go_get_stage_instance(pipeline_name, pipeline_counter, stage_name):
    return requests.get(
        api_go_url + "stages/" + pipeline_name + "/" + stage_name + "/instance/" + str(pipeline_counter) + "/1",
        auth=auth).content


def go_request_stages_history(pipeline_name, pipeline_id, stage, stage_name):
    return requests.get(
        api_go_url + "stages/" + pipeline_name + "/" + stage_name + "/instance/" + str(pipeline_id) + "/" + str(stage),
        auth=auth).content


def go_get_agent_information(agent_uuid):
    return requests.get(api_go_url + "agents/" + agent_uuid, auth=auth,
                        headers={"Accept": "application/vnd.go.cd.v2+json"})


def go_request_junit_report(pipeline_name, pipeline_id, stage, stage_name):
    return requests.get(base_go_url + "files/" + pipeline_name + "/" + str(pipeline_id)
                        + "/" + stage_name + "/" + str(stage) + "/defaultJob/testoutput/index.html", auth=auth).content.decode("utf-8")


def go_request_job_history(pipeline_name, stage_name, offset=0):
    return requests.get(api_go_url + "jobs/" + pipeline_name + "/" + stage_name + "/defaultJob/history/" + str(offset),
                        auth=auth).content


def go_request_console_log(pipeline_name, pipeline_id, stage_index, stage_name):
    return requests.get(base_go_url + "files/" + pipeline_name + "/" + str(pipeline_id)
                        + "/" + stage_name + "/" + str(stage_index) + "/defaultJob/cruise-output/console.log",
                        auth=auth).content.decode("utf-8")


def go_request_comparison_html(pipeline_name, current, comparison):
    return requests.get(base_go_url + "compare/{}/{}/with/{}".format(pipeline_name, current, comparison),
                 auth=auth).content.decode('utf-8', 'ignore')