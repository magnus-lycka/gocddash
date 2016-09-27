#!/usr/bin/env python3
import os
import psutil
import random
import socket
import subprocess
import sys
import time
import requests


def get_free_port():
    # There is a potential for a race condition here, but I think it works ok in practice.
    port_used = True
    while port_used:
        port = random.randrange(4545, 9999)
        port_used = port in [x.laddr[1] for x in psutil.net_connections()]
    # noinspection PyUnboundLocalVariable
    return port


def start_servers(gocd_dash_path):
    application_port = get_free_port()
    print("starting server, application on port {}, using checkout {}".format(application_port, gocd_dash_path))

    apply_db_migrations(gocd_dash_path)
    application_process = start_application(gocd_dash_path, None, application_port)

    return application_port, application_process


def do_get(url, data):
    try:
        return subprocess.check_output(["/usr/bin/lynx", "-dump", url], stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as error:
        print(error)
        print(error.output.decode("UTF-8"))
        raise


def do_post(url, data):
    response = requests.post(url, data)
    return response.text.encode("UTF-8")


def perform_testcase(port):
    action = {
        'GET': do_get,
        'POST': do_post,
    }
    print("Starting test workflow for GO CD Dashboard")
    with open("gui_log.txt", "w", encoding="UTF-8") as log:
        with open("urls.txt") as rows:

            coverage_url = "http://127.0.0.1:{}/dash/coverage/".format(port)

            for row in rows:
                verb, url, *raw_data = row.split()
                data = dict(pair.split('=') for pair in raw_data)
                url = url.format(port=port)
                log.write("{} {}\ndata: {}\n".format(verb, url, data))
                out = action[verb](url, data)
                log.write(out.decode("UTF-8"))

            requests.get(coverage_url)


def stop_servers(application):
    application.kill()


def main():
    python_version = sys.version_info.major
    if not (3 == python_version):
        print("This code requires Python 3. Instead found version {}. Exiting.".format(python_version))
        sys.exit(-1)
    gocd_dash_path = os.environ['TEXTTEST_CHECKOUT']
    app_port, application = start_servers(gocd_dash_path)
    try:
        sync_pipelines(gocd_dash_path)
        perform_testcase(app_port)
    finally:
        stop_servers(application)


def apply_db_migrations(gocd_dash_path):
    os.system('sqlite3 gocddash.sqlite3 < {}'.format(gocd_dash_path + '/migrations/setup.sql'))


def start_application(gocd_dash_path, db_port, application_port):
    application_process = subprocess.Popen(["/usr/bin/env", "python3",
                                            gocd_dash_path + "/gocddash/app.py",
                                            "-b", str(application_port),
                                            "--db-port", str(db_port),
                                            "--file-client", os.getcwd(),
                                            "--pipeline-config", os.getcwd() + "/pipelines.json"])

    _wait_for_app_to_start(application_port)
    return application_process


def _wait_for_app_to_start(application_port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def can_connect():
        try:
            s.connect(('localhost', application_port))
            return True
        except socket.error:
            return False

    i = 0
    while i < 10 and not can_connect():
        time.sleep(.5)
        i += 1
    s.close()
    print("application is started")


def sync_pipelines(gocd_dash_path):
    subprocess.check_call(["/usr/bin/env", "coverage3",
                           "run",
                           "--branch",
                           "--parallel-mode",
                           "--source=gocddash",
                           gocd_dash_path + "/sync_pipelines.py",
                           "--db-port", str(0),
                           "-a", os.getcwd() + "/application.cfg",
                           "-p", os.getcwd() + "/pipelines.json",
                           "-f", os.getcwd()])
    print("pipelines are synced")


if __name__ == "__main__":
    main()
