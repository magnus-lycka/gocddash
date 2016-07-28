import time

from gocddash import parse_cctray
from gocddash.analysis.go_client import get_client


class PipelineStatusCache:
    def __init__(self):
        self.latest_synced = 0
        self.pipelines = []

    def get_pipelines(self):
        current_time = int(round(time.time() * 1000))
        if current_time - self.latest_synced > 60000:
            project = get_cctray_status()
            self.pipelines = project.select(
                'failing')
            self.latest_synced = current_time

        return self.pipelines


_pipeline_status_cache = None

def get_cctray_status():
    xml = get_client().go_get_cctray()
    project = parse_cctray.Projects(xml)
    return project


def create_cache():
    global _pipeline_status_cache
    if not _pipeline_status_cache:
        _pipeline_status_cache = PipelineStatusCache()
    return _pipeline_status_cache


def get_cache():
    if not _pipeline_status_cache:
        raise ValueError("Pipeline status cache not instantiated")
    return _pipeline_status_cache