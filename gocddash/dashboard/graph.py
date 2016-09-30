"""Handles all the graphing and plotting used in the various graphs of the dashboard"""

from collections import defaultdict, Counter, namedtuple

from gocddash.analysis.domain import get_graph_statistics_for_final_stages, \
    get_graph_statistics

GREEN = '#5ab738'
RED = '#f22c40'
BLUE = '#2176ff'
YELLOW = '#eac435'


def agent_success_rates(days_limit=0, count_limit=0, pipeline=None):
    """
    Summarize outcomes of all jobs executed per agent.
    The summary can be limited to the last `count_limit` jobs and/or the last `days_limit` days.
    Returns a dictionary keyed by `agent name` and values with attributes .n, .success,
    .test, .startup and .post .
    """
    Summary = namedtuple('Summary', ['n', 'success', 'test', 'startup', 'post'])
    jobs = defaultdict(list)
    results = {}
    for job in get_graph_statistics(days_limit, pipeline):
        jobs[job.agent_name].append((job.scheduled_date, job.failure_stage or 'SUCCESS'))
    for agent, job_list in jobs.items():
        job_list.sort()
        job_list = job_list[-count_limit:]
        n = len(job_list)
        count = Counter(job[1] for job in job_list)
        results[agent] = Summary(n, count['SUCCESS'], count['TEST'], count['STARTUP'], count['POST'])
    return results


def pipeline_test_results(pipeline_name):
    """
    Creates data for a graph showing the historical tests run of a
    specific pipeline split up into passed, failed, and skipped tests
    :param pipeline_name: the name of the requested pipeline
    :return: a dictionary keyed by `pipeline counter` and values with attributes .n, .success,
    .test, .startup and .post .
    """
    Summary = namedtuple('Summary', ['passed', 'failed', 'skipped'])
    results = {}
    for run in get_graph_statistics_for_final_stages(pipeline_name):
        results[run.pipeline_counter] = Summary(
            run.tests_run - run.tests_failed - run.tests_skipped,
            run.tests_failed,
            run.tests_skipped
        )
    return results
