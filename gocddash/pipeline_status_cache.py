import time

from gocddash.analysis.domain import get_cctray_status


class PipelineStatusCache:
    def __init__(self):
        self.latest_synced = 0
        self.pipelines = []

    def get_pipelines(self):
        current_time = int(round(time.time() * 1000))
        if current_time - self.latest_synced > 6000000:
            project = get_cctray_status()
            self.pipelines = project.select(
                'failing')
            self.latest_synced = current_time

        return self.pipelines


_pipeline_status_cache = None


def create_cache():
    global _pipeline_status_cache
    if not _pipeline_status_cache:
        _pipeline_status_cache = PipelineStatusCache()
    return _pipeline_status_cache


def get_cache():
    if not _pipeline_status_cache:
        raise ValueError("Pipeline status cache not instantiated")
    return _pipeline_status_cache