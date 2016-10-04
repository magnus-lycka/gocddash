"""Handles all the graphing and plotting used in the various graphs of the dashboard"""

from collections import defaultdict, Counter, namedtuple

from gocddash.analysis.domain import get_graph_statistics_for_final_stages, get_graph_statistics

GREEN = '#5ab738'
RED = '#f22c40'
BLUE = '#2176ff'
YELLOW = '#eac435'


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


def pipeline_history_chart_json(pipeline_name):
    pipeline_summaries = pipeline_test_results(pipeline_name)
    title = "Historical tests for {}. (last {} executions)".format(pipeline_name, len(pipeline_summaries))

    def make_bar_row(label, color, x, y):
        return {
            "x": x,
            "y": y,
            "name": label,
            "type": "bar",
            "marker": {"color": color }
        }

    data = []
    x = sorted(pipeline_summaries)
    for label, color in [
        ('passed', GREEN),
        ('failed', RED),
        ('skipped', BLUE),
    ]:
        y = [getattr(pipeline_summaries[pipeline_counter], label.lower()) for pipeline_counter in x]
        data.append(make_bar_row('Tests ' + label, color, x, y))
    return layout(title, "Pipeline counter", "Test-count"), data


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


def agent_success_rate_chart_json(limit_cnt, limit_days, percentage, pipeline):
    if pipeline:
        title = "Historical agent success rate for pipeline {}. ".format(pipeline)
    else:
        title = "Historical agent success rate for all pipelines. "

    if limit_days:
        title += "Max {} days. ".format(limit_days)

    if limit_cnt:
        title += "Max {} jobs per agent. ".format(limit_cnt)

    agent_summaries = agent_success_rates(limit_days, limit_cnt, pipeline)

    def make_bar_row(label, color, x, y, n, percentage=False):
        if percentage:
            template = "\nFailure stage: {}\nTotal tests run on agent: {}"
            text = [template.format(label, nn) for (yy, nn) in zip(y, n)]
        else:
            template = "\nFailure stage: {}\nRate: {:.1f}%\nTotal tests run on agent: {}"
            text = [template.format(label, 100.0 * yy / nn, nn) for (yy, nn) in zip(y, n)]
        return {
            "x": x,
            "y": y,
            "name": label,
            "type": "bar",
            "text": text,
            "marker": {"color": color }
        }

    y_maker = getattr
    y_label = 'Jobs (count)'

    if percentage:

        def y_maker(summary, kind):
            if summary.n:
                return 100.0 * getattr(summary, kind) / summary.n
            else:
                return 0.0

        y_label = 'Jobs (percent)'

    x_label = "Agent name"
    data = []
    x = sorted(agent_summaries)
    for label, color in [
        ('Success', GREEN),
        ('Test', RED),
        ('Startup', BLUE),
        ('Post', YELLOW),
    ]:
        y = [y_maker(agent_summaries[agent], label.lower()) for agent in x]
        n = [agent_summaries[agent].n for agent in x]
        data.append(make_bar_row(label, color, x, y, n, percentage))
    return layout(title, x_label, y_label), data


def layout(title, x_label, y_label):
    return {
        "hovermode": "closest",
        "barmode": "stack",
        "title": title,
        "legend": {
            "x": 0,
            "y": 100,
            "orientation": "h"
        },
        "xaxis": {
            "title": x_label
        },
        "yaxis": {
            "title": y_label
        }
    }
