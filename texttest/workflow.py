#/usr/bin/env python3

def start_servers():
    # start db docker on unique port
    # load data into db from flat files in test case
    # start the dashboard server on unique port
    db_port = 15554 # TODO: make the db port configurable in data_access.py so it can be set on the command line
    application_port = 5000

    return db_port, application_port

def stop_servers(db_port, application_port):
    # stop the dasboard server
    # stop the db docker
    pass

def perform_testcase():
    print "Starting test workflow for GO CD Dashboard"
    with open("gui_log.txt", "w") as log:
        with open("urls.txt") as urls:
            for url in urls:
                log.write("url: {}".format(url))
                # navigate to the url
                # make ascii art of the page
                # store the ascii art in the 'gui_log.txt' file
                log.write("store the ascii art here")

def main():
    db_port, application_port = start_servers()
    try:
        perform_testcase()
    finally:
        stop_servers(db_port, application_port)


if __name__ == "__main__":
    main()
