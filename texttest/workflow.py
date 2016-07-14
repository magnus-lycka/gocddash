#!/usr/bin/env python3

import subprocess

from docker_management import ContainerManager


def start_servers(docker):
    # start db docker on unique port
    # load data into db from flat files in test case
    # start the dashboard server on unique port
    db_port = 15550 # TODO: make the db port configurable in data_access.py so it can be set on the command line
    db_container = _start_db_docker(docker, db_port)

    application_port = 5000
    application_process = None # TODO: start application

    return db_container, application_process

def stop_servers(docker, db, application):
    # stop the dasboard server
    # stop the db docker
    docker.stop_container(db)

def perform_testcase():
    print("Starting test workflow for GO CD Dashboard")
    with open("gui_log.txt", "w") as log:
        with open("urls.txt") as urls:
            for url in urls:
                log.write("url: {}".format(url))
                # navigate to the url
                # make ascii art of the page
                # store the ascii art in the 'gui_log.txt' file
                sprocess_call = subprocess.Popen(["/usr/bin/lynx", "-dump", url], stdout=subprocess.PIPE)
                out = sprocess_call.communicate()[0]
                log.write(out)

def main():
    docker = ContainerManager("dockerregistry.pagero.local") # TODO: Put this image on docker hub instead of our internal docker registry
    db, application = start_servers(docker)
    try:
        perform_testcase()
    finally:
        stop_servers(docker, db, application)

def _start_db_docker(docker, dbport):
    db_image = "go-analysis-db"
    db_image_tag = "1.1.1-GO"

    return docker.start_db_container(db_image, db_image_tag, dbport)


if __name__ == "__main__":
    main()
