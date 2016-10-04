#!/usr/bin/env python3
import os
import psutil
import random
import socket
import subprocess
import sys
import time
import requests
# noinspection PyPackageRequirements
import bs4


def executable(binary='python'):
    candidates = [
        os.path.join(sys.exec_prefix, 'bin', binary),
        os.path.join(sys.exec_prefix, 'local', 'bin', binary),
    ]
    for candidate in candidates:
        if os.path.exists(candidate):
            return candidate
    raise ValueError("Can't find location of {}".format(binary))


def get_free_port():
    # There is a potential for a race condition here, but I think it works ok in practice.
    port_used = True
    while port_used:
        port = random.randrange(4545, 9999)
        port_used = port in [x.laddr[1] for x in psutil.net_connections()]
    # noinspection PyUnboundLocalVariable
    return port


def text_from_html(html):
    soap = bs4.BeautifulSoup(html, 'lxml')
    text = soap.get_text("\n", strip=True)
    return text


def start_servers(gocd_dash_path):
    application_port = get_free_port()
    print("starting server, application on port {}, using checkout {}".format(application_port, gocd_dash_path))

    #init_database(gocd_dash_path)
    application_process = start_application(None, application_port)

    return application_port, application_process


# noinspection PyUnusedLocal
def do_get(url, data):
    try:
        # noinspection PyUnresolvedReferences
        return subprocess.check_output(["/usr/bin/lynx", "-dump", url], stderr=subprocess.STDOUT).decode('utf-8')
    except subprocess.CalledProcessError as error:
        print(error)
        print(error.output)
        raise


def do_post(url, data):
    response = requests.post(url, data)
    return text_from_html(response.text)


def run_shell_script(script, _):
    # noinspection PyUnresolvedReferences
    return subprocess.check_output([script], stderr=subprocess.STDOUT).decode('utf-8')


def perform_testcase(port):
    action = {
        'GET': do_get,
        'POST': do_post,
        'SHELL': run_shell_script,
    }
    print("Starting test workflow for GO CD Dashboard")
    with open("gui_log.txt", "w", encoding="utf-8") as log:
        with open("actions.txt") as rows:

            coverage_url = "http://127.0.0.1:{}/dash/coverage/".format(port)

            for row in rows:
                if not row.strip():
                    continue
                verb, url, *raw_data = row.split()
                data = dict(pair.split('=') for pair in raw_data)
                url = url.format(port=port)
                log.write("{} {}\ndata: {{{}}}\n".format(verb, url,
                                                         ", ".join("%s='%s'" % tup for tup in sorted(data.items()))))
                out = action[verb](url, data)
                try:
                    log.write(out)
                except TypeError as err:
                    print("Got '{}' on log.write()".format(err))
                    print("What I had:", verb, url, data, type(out))
                    print("What I got back:", out.decode('utf-8'))
                    raise

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
        sync_pipelines()
        perform_testcase(app_port)
    finally:
        stop_servers(application)


def init_database(gocd_dash_path):
    os.system('sqlite3 gocddash.sqlite3 < {}'.format(gocd_dash_path + '/gocddash/database/setup.sql'))


def start_application(db_port, application_port):
    application_process = subprocess.Popen([executable(),
                                            executable("gocddash_app.py"),
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


def sync_pipelines():
    os.makedirs('/tmp/gocddash-cover/', exist_ok=True)
    subprocess.check_call([executable('coverage'),
                           "run",
                           "--branch",
                           "--parallel-mode",
                           "--source=gocddash",
                           executable("gocddash_sync.py"),
                           "--db-port", str(0),
                           "-a", os.getcwd() + "/application.cfg",
                           "-p", os.getcwd() + "/pipelines.json",
                           "-f", os.getcwd()])
    print("pipelines are synced")


if __name__ == "__main__":
    main()
