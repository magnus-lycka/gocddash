import os
import json
import requests
import sqlite3
import time
import datetime


def fetch_agents():
    go_server = os.environ.get('GO_SERVER', 'http://localhost:8153')
    go_user = os.environ.get('GO_USER')
    go_passwd = os.environ.get('GO_PASSWD')
    kwargs = {}
    if go_user:
        kwargs['auth'] = (go_user, go_passwd)
    r = requests.get(go_server + '/go/api/agents', **kwargs)
    assert r.status_code == 200, r
    return json.loads(r.content)


def fetch_agent_jobs(agent, offset):
    go_server = os.environ.get('GO_SERVER', 'http://localhost:8153')
    go_user = os.environ.get('GO_USER')
    go_passwd = os.environ.get('GO_PASSWD')
    kwargs = {}
    if go_user:
        kwargs['auth'] = (go_user, go_passwd)
    url = go_server + '/go/api/agents/%s/job_run_history/%i' % (agent, offset)
    r = requests.get(url, **kwargs)
    assert r.status_code == 200, r
    return json.loads(r.content)


def init_db(conn):
    tables = [
        """CREATE TABLE AGENTS (
        UUID TEXT NOT NULL,
        NAME TEXT NOT NULL,
        IPADDR TEXT NOT NULL,
        PRIMARY KEY (UUID)
    )""",

        """CREATE TABLE JOBS (
        ID TEXT NOT NULL,
        AGENT_UUID TEXT NOT NULL,
        NAME TEXT NOT NULL,
        PIPELINE_NAME TEXT NOT NULL,
        STAGE_NAME TEXT NOT NULL,
        SCHEDULED TIMESTAMP NOT NULL,
        PRIMARY KEY (ID)
    )""",

        """CREATE TABLE JOB_STATE_CHANGES (
        ID TEXT NOT NULL,
        JOB_ID TEXT NOT NULL,
        STATE TEXT NOT NULL,
        TSMILLIS NUMBER NOT NULL,
        PRIMARY KEY (ID)
    )""",
    ]
    for table in tables:
        try:
            cur = conn.cursor()
            cur.execute(table)
            conn.commit()
            print " ".join(table.split()[:3]).capitalize()
        except sqlite3.OperationalError as err:
            if 'exists' in err.message:
                print "Table", table.split()[2], 'existed'
            else:
                raise


def update_agent(dbpath, agent):
    sql = "INSERT OR REPLACE INTO AGENTS (UUID, NAME, IPADDR) VALUES (?, ?, ?)"
    conn = sqlite3.connect(dbpath)
    cur = conn.cursor()
    print sql
    print agent
    cur.execute(sql, (agent['uuid'], agent['agent_name'], agent['ip_address']))
    conn.commit()
    conn.close()


def store_jobs(dbpath, jobs):
    done = False
    sql_jobs = """INSERT INTO JOBS (ID, AGENT_UUID, NAME, PIPELINE_NAME, STAGE_NAME, SCHEDULED)
                  VALUES (?, ?, ?, ?, ?, ?)"""
    sql_change = """INSERT OR REPLACE INTO JOB_STATE_CHANGES (ID, JOB_ID, STATE, TSMILLIS)
                    VALUES (?, ?, ?, ?)"""
    conn = sqlite3.connect(dbpath)
    cur = conn.cursor()
    for job in jobs:
        ts = datetime.timedelta(seconds=job['scheduled_date'] / 1000.) + datetime.datetime(1970, 1, 1, 0, 0, 0)
        try:
            cur.execute(
                sql_jobs,
                (job['id'], job['agent_uuid'], job['name'], job['pipeline_name'], job['stage_name'], ts))
        except sqlite3.IntegrityError as err:
            if 'UNIQUE' in err.message:
                done = True
            else:
                raise
        for state_change in job["job_state_transitions"]:
            cur.execute(
                sql_change,
                (state_change['id'], job['id'], state_change['state'], state_change['state_change_time'],))
    conn.commit()
    conn.close()
    return done


def main():
    dbpath = 'gocdmon.sqlite'
    conn = sqlite3.connect(dbpath)
    init_db(conn)
    conn.close()
    while True:
        for agent in fetch_agents():
            update_agent(dbpath, agent)
            offset = 0
            while 1:
                data = fetch_agent_jobs(agent['uuid'], offset)
                jobs = data['jobs']
                pagination = data['pagination']
                if not jobs:
                    break
                done = store_jobs(dbpath, jobs)
                if done:
                    break
                offset += pagination["page_size"]
        time.sleep(1000)


if __name__ == '__main__':
    main()
