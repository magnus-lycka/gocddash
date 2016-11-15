from gocddash.analysis import go_client
from bs4 import BeautifulSoup as Bs
from collections import Counter
import json
import re

go = go_client.GoClient('http://go.pagero.local/go/', ('dash', 'board'))


def get_pipelines(go):
    pipelines = []
    result = json.loads(go.get_pipeline_groups())
    for pipeline_grp in result:
        pipelines.extend([p['name'] for p in pipeline_grp['pipelines']])
    return pipelines


def get_jobs(go, pipeline):
    jobs = []
    for offset in range(5):
        pl_hist = json.loads(go.request_pipeline_history(pipeline, offset))
        for p in pl_hist['pipelines']:
            p_counter = p['counter']
            for s in p['stages']:
                stage = s['name']
                s_counter = s['counter']
                for job in s['jobs']:
                    jobs.append((
                        pipeline,
                        p_counter,
                        s_counter,
                        stage,
                        job['name']
                    ))
    return jobs


def test_report(go, job):
    try:
        html = go.request_junit_report(*job)[1]
        #print('Made report for', job)
        return Bs(html, 'html.parser')
    except LookupError:
        #print('No report for', job)
        pass


def test_report_finder():
    for pipeline in get_pipelines(go):
        for job in get_jobs(go, pipeline):
            yield test_report(go, job)


def clean(text):
    if not text:
        return text
    return re.sub('\(\d+\)', '(NNN)', text).strip()


def extract(soap, summary, heading):
    if soap:
        for span in soap.p.find_all('span'):
            for cls in span['class']:
                summary[cls] += 1

        for tr in soap.find_all('tr'):
            heading[clean(tr.td.string)] += 1


summary = Counter()
heading = Counter()


for report in test_report_finder():
    extract(report, summary, heading)


print(summary)
print(heading)

# Counter({'tests_total_count': 939, 'tests_ignored_count': 939, 'tests_total_duration': 939, 'tests_failed_count': 939})
# Counter({None: 16020, 'Type:': 7474, 'Message:': 7474, 'Test:': 7474, 'Failure': 7313, 'All Tests Passed': 747, 'Error': 161, 'Unit Test Failure and Error Details (NNN)': 133, "This project doesn't have any tests": 59, 'No Tests Run': 59})
