from __future__ import division
from flask import Flask
from jinja2 import Environment, FileSystemLoader
import sqlite3
import datetime
import time
from collections import defaultdict, OrderedDict
from jobqueue import SAMPLES_MARKER

app = Flask(__name__)
env = Environment(loader=FileSystemLoader('templates'))


class JobStateChanges(object):
    def __init__(self, dbpath):
        self.millis_two_weeks_ago = 1000 * (time.time() - 14 * 24 * 60 * 60)
        self.millis_one_week_ago = 1000 * (time.time() - 7 * 24 * 60 * 60)
        self.millis_one_day_ago = 1000 * (time.time() - 24 * 60 * 60)
        self.millis_one_hour_ago = 1000 * (time.time() - 60 * 60)
        self.dbpath = dbpath
        self._job_state_changes = []

    def fetch(self):
        select = """SELECT JOB_ID, STATE, TSMILLIS FROM JOB_STATE_CHANGES
        WHERE TSMILLIS > ? ORDER BY JOB_ID, TSMILLIS"""
        conn = sqlite3.connect(self.dbpath)
        cur = conn.cursor()
        self._job_state_changes = list(cur.execute(select, (self.millis_two_weeks_ago,)))
        conn.close()

    @property
    def phasetimes(self):
        result = OrderedDict()
        result['Last week'] = OrderedDict()
        result['Last 24 h'] = OrderedDict()
        result['Last hour'] = OrderedDict()
        last_state = None
        last_millis = None
        last_job = None
        states = "Scheduled Assigned Preparing Building Completing Completed".split()
        order = []
        for i, start in enumerate(states[:-1]):
            for stop in states[i + 1:]:
                order.append("{} => {}".format(start, stop))
        for key in order:
            for period in result:
                result[period][key] = 0.0
        for job, state, millis in self._job_state_changes:
            if job == last_job:
                if millis > self.millis_one_week_ago:
                    result['Last week']['%s => %s' % (last_state, state)] += millis - last_millis
                if millis > self.millis_one_day_ago:
                    result['Last 24 h']['%s => %s' % (last_state, state)] += millis - last_millis
                if millis > self.millis_one_hour_ago:
                    result['Last hour']['%s => %s' % (last_state, state)] += millis - last_millis
            last_job = job
            last_millis = millis
            last_state = state
        return result


class JobQData(object):
    def __init__(self, dbpath):
        self.dbpath = dbpath
        self.columns = []
        self.rows = []

    def fetch(self):
        start = datetime.datetime.now() - datetime.timedelta(days=2)
        select = """SELECT TIMEOFDAY, WHAT, HOWMUCH FROM JOBQHIST
        WHERE TIMEOFDAY > ?"""
        conn = sqlite3.connect(self.dbpath)
        cur = conn.cursor()
        results = list(cur.execute(select, (start,)))
        conn.close()
        sums = defaultdict(int)
        maximum = defaultdict(int)
        counts = defaultdict(int)
        hours = set()
        params = set()
        max_hour = '0'
        min_hour = '9'
        for when, what, count in results:
            hour = self.round_to_hour(when)
            hours.add(hour)
            max_hour = max(max_hour, hour)
            min_hour = min(min_hour, hour)
            sums[(hour, what)] += count
            maximum[(hour, what)] = max(count, maximum[(hour, what)])
            if what == SAMPLES_MARKER:
                counts[hour] += count
            else:
                params.add(what)
        self.set_cols(params)
        for hour in sorted(hours):
            row = ["'%s'" % hour]
            for param in sorted(params):
                row.append(maximum.get((hour, param), 0))
                row.append(sums.get((hour, param), 0) / counts.get(hour, 1))
            self.rows.append(row)

    def set_cols(self, params):
        self.columns = [('string', 'Hour')]
        for param in sorted(params):
            self.columns.append(('number', 'Max ' + param))
            self.columns.append(('number', 'Mean ' + param))

    @staticmethod
    def round_to_hour(ts):
        if isinstance(ts, datetime.datetime):
            return ts.strftime('%Y-%m-%d %H')
        else:
            # Assume string
            return ts[:13]


pages = [
    ('/', 'Index'),
    ('/jobqhist', 'Job Queue History'),
    ('/phasetime', 'Time in Job Phases'),
]


@app.route('/jobqhist')
def jobqhist():
    data = JobQData('gocdmon.sqlite')
    data.fetch()
    return env.get_template("jobqhist.html").render(jobqdata=data, pages=pages)


@app.route('/phasetime')
def phasetime():
    data = JobStateChanges('gocdmon.sqlite')
    data.fetch()
    return env.get_template("phasetime.html").render(data=data.phasetimes, pages=pages)


@app.route('/')
def index():
    return env.get_template("index.html").render(pages=pages)


if __name__ == '__main__':
    app.run(debug=True)
