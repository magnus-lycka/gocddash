#!/usr/bin/env python3

import subprocess

from docker_management import ContainerManager
import os
import random

def start_servers(docker):
    # db_port = 15550
    # db_container = _start_db_docker(docker, db_port)
    application_port = random.randrange(4545, 4999)
    gocd_dash_path = os.environ['gocd_dash']
    application_process = subprocess.Popen(["/usr/bin/env", "python3", gocd_dash_path + "gocddash/app.py", "-b", str(application_port), "--db-port", str(15554), "--file-client",
                                            os.getcwd()])

    subprocess.Popen(["/usr/bin/env", "python3", gocd_dash_path + "sync_pipelines.py", "-a", os.getcwd() + "/application.cfg", "-p", os.getcwd() + "/pipelines.json", "-f", os.getcwd()])

    # return db_container, application_process
    return None, application_port, application_process


def stop_servers(docker, db, application):
    application.kill()
    # docker.stop_container(db)


def perform_testcase(port):
    print("Starting test workflow for GO CD Dashboard")
    with open("gui_log.txt", "w") as log:
        with open("urls.txt") as urls:
            for url in urls:
                url_contents = url.split(':')
                protocol = url_contents[0]
                host = url_contents[1]
                path = url_contents[2][4:]
                url = protocol + ":" + host + ":" + str(port) + path

                log.write("url: {}".format(url))
                # navigate to the url
                # make ascii art of the page
                # store the ascii art in the 'gui_log.txt' file
                sprocess_call = subprocess.Popen(["/usr/bin/lynx", "-dump", url], stdout=subprocess.PIPE)
                out = sprocess_call.communicate()[0]
                log.write(out)


def main():
    docker = ContainerManager(
        "dockerregistry.pagero.local")  # TODO: Put this image on docker hub instead of our internal docker registry
    db, app_port, application = start_servers(docker)
    import time
    try:
        time.sleep(2)
        perform_testcase(app_port)
    finally:
        stop_servers(docker, db, application)


def _start_db_docker(docker, dbport):
    db_image = "go-analysis-db"
    db_image_tag = "1.1.1-GO"

    return docker.start_db_container(db_image, db_image_tag, dbport)


if __name__ == "__main__":
    main()
