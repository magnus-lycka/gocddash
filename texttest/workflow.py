#!/usr/bin/env python3

import os, sys
import random
import subprocess
import time
import socket
import psycopg2

from docker_management import ContainerManager
from yoyo import read_migrations, get_backend

def start_servers(docker):
    db_port =  random.randrange(15550, 17550)
    application_port = random.randrange(4545, 4999)
    gocd_dash_path = os.environ['TEXTTEST_CHECKOUT']
    print("starting servers, db on port {} and application on port {}, using checkout {}".format(db_port, application_port, gocd_dash_path))

    db_container = start_db_docker(docker, db_port)
    apply_db_migrations(gocd_dash_path, db_port)
    application_process = start_application(gocd_dash_path, db_port, application_port)
    sync_pipelines(gocd_dash_path, db_port)

    return db_container, application_port, application_process

def perform_testcase(port):
    print("Starting test workflow for GO CD Dashboard")
    with open("gui_log.txt", "w", encoding="UTF-8") as log:
        with open("urls.txt") as urls:
            for url in urls:
                url_contents = url.split(':')
                protocol = url_contents[0]
                host = url_contents[1]
                path = url_contents[2][4:]
                url = protocol + ":" + host + ":" + str(port) + path

                log.write("url: {}\n".format(url))

                out = subprocess.check_output(["/usr/bin/lynx", "-dump", url])
                log.write(out.decode("UTF-8"))

def stop_servers(docker, db, application):
    application.kill()
    docker.stop_container(db)

def main():
    python_version = sys.version_info.major
    if not (3 == python_version):
        print("This code requires Python 3. Instead found version {}. Exiting.".format(python_version))
        sys.exit(-1)
    docker = ContainerManager()
    db, app_port, application = start_servers(docker)
    try:
        perform_testcase(app_port)
    finally:
        stop_servers(docker, db, application)


def start_db_docker(docker, dbport):
    db_image = "postgres"
    db_image_tag = "9.3"
    db_params = {"POSTGRES_PASSWORD":"analysisappluser",
                 "POSTGRES_USER":"analysisappluser",
                 "POSTGRES_DB": "go-analysis"}

    db_container = docker.start_db_container(db_image, db_image_tag, dbport, environment=db_params)
    return db_container

def apply_db_migrations(gocd_dash_path, db_port):
    conn_str = 'postgresql://analysisappluser:analysisappluser@dev.localhost:{}/go-analysis'.format(db_port)
    _wait_for_db_to_accept_connections(conn_str)
    backend = get_backend(conn_str)
    migrations = read_migrations(gocd_dash_path + '/migrations')
    backend.apply_migrations(backend.to_apply(migrations))

def _wait_for_db_to_accept_connections(conn_str):
    def can_connect():
        try:
            get_backend(conn_str)
            return True
        except psycopg2.OperationalError:
            return False
    i = 0
    while i < 10 and not can_connect():
        time.sleep(0.5)
        i += 1
    print("db is accepting connections")

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
        except socket.error as e:
            return False
    i = 0
    while i < 10 and not can_connect():
        time.sleep(.5)
        i += 1
    s.close()
    print("application is started")

def sync_pipelines(gocd_dash_path, db_port):
    subprocess.check_call(["/usr/bin/env", "python3",
                     gocd_dash_path + "/sync_pipelines.py",
                     "--db-port", str(db_port),
                     "-a", os.getcwd() + "/application.cfg",
                     "-p", os.getcwd() + "/pipelines.json",
                     "-f", os.getcwd()])
    print("pipelines are synced")

if __name__ == "__main__":
    main()
