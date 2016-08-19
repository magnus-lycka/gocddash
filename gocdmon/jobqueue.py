import datetime
import os
import sqlite3
import time
from collections import defaultdict
from xml.etree import ElementTree as Et

import requests

SAMPLES_MARKER = 'meta:measurement'


def analyze_xml(data):
    ts = datetime.datetime.now()
    print(data)
    environments = defaultdict(int)
    resources = defaultdict(int)
    root = Et.fromstring(data)
    for job in root.findall('job'):
        env = job.find('environment')
        env_text = env.text if env is not None else '--none--'
        environments[env_text] += 1
        for resource in job.findall('resources/resource'):
            resources[resource.text] += 1
    results = [(ts, SAMPLES_MARKER, 1)]
    for environment, count in environments.items():
        results.append((ts, 'environment:' + environment, count))
    for resource, count in resources.items():
        results.append((ts, 'resource:' + resource, count))
    return results


def fetch_jobqueue():
    GO_SERVER = os.environ.get('GO_SERVER', 'http://localhost:8153')
    GO_USER = os.environ.get('GO_USER')
    GO_PASSWD = os.environ.get('GO_PASSWD')
    kwargs = {}
    if GO_USER:
        kwargs['auth'] = (GO_USER, GO_PASSWD)

    r = requests.get(GO_SERVER + '/go/api/jobs/scheduled.xml', **kwargs)
    return analyze_xml(r.content)


def init_db(conn):
    tables = [
        """CREATE TABLE JOBQHIST (
        TIMEOFDAY TIMESTAMP NOT NULL,
        WHAT VARCHAR(100) NOT NULL,
        HOWMUCH INT NOT NULL,
        PRIMARY KEY (TIMEOFDAY, WHAT)
    )""",

    ]
    for table in tables:
        try:
            cur = conn.cursor()
            cur.execute(table)
            conn.commit()
            print(" ".join(table.split()[:3]).capitalize())
        except sqlite3.OperationalError as err:
            if 'exists' in err.message:
                print("Table", table.split()[2], 'existed')
            else:
                raise


def store(dbpath, data):
    conn = sqlite3.connect(dbpath)
    cur = conn.cursor()
    for timeofday, what, howmuch in data:
        cur.execute('INSERT INTO JOBQHIST VALUES (?, ?, ?)',
                    (timeofday, what, howmuch))
    conn.commit()
    conn.close()


def main():
    dbpath = 'gocdmon.sqlite'
    conn = sqlite3.connect(dbpath)
    init_db(conn)
    conn.close()
    while True:
        time.sleep(60 - time.localtime()[5])
        data = fetch_jobqueue()
        print(data)
        store(dbpath, data)


if __name__ == '__main__':
    main()
