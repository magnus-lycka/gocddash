# gocddash
Status dashboard for Go.CD Continuous Delivery Server

Gocddash provides an overview of the builds in your
Thoughtworks Go Continuous Delivery server.

You select which pipeline groups you want to monitor,
and whether you only want to see failing builds,
failing builds plus currently building, or all builds.
The builds you selected will be shown in descending
chronological order.

By default, you just see the pipeline name, the current
status, the pipeline label and the latest build time,
but you can expand the view to see the status of its
stages and jobs, as well as the list of breakers.
There are also links to the current versions of pipelines,
stages and jobs at the go-server.

Gocddash uses the cctray.xml file from the go-server.

## Why gocddash? Why not buildreactor?

We wrote gocddash to have clear information radiators regarding
GoCD builds on large screens in developer team rooms.

Since these large screens were Smart TVs with builtin web
browsers (which were not Google Chrome) we wanted something
running as a web service rather than a Chrome plugin.

Gocddash is different than buildreactor in several ways:

 - It only works with GoCD. No Jenkins, Bamboo or Travis etc.
 - No pop-up alerts, just the dashboard.
 - It understands the difference between Pipelines, Stages and Jobs, and show them in the correct hierarchy.
 - It understands Pipeline Groups, and lets you select the groups you are interested in seeing, rather than the mess of maybe hundreds of stages and jobs.
 - It sorts Pipelines by build time and shows the most recent on the top.
 - You can select if you only want to see broken Pipelines, brooken + currently building, or all Pipelines.
 - It understands paused Pipelines and greys them out.
 - It shows you the Pipeline counters, the Stage counters, and a timestamp for the latest build.
 - It needs to be installed and run on some server...
 - It has plenty of themes.

## Usage

    usage: app.py [-h] [-s SERVER] [-u USER] [-p PASSWD] [-d] [-c {1,2,3,4}]

    optional arguments:
        -h, --help           show this help message and exit
        -s SERVER, --server SERVER
                             go server url
        -u USER, --user USER  go server user name
        -p PASSWD, --passwd PASSWD
                             go server password
        -d, --debug
        -c {1,2,3,4}, --columns {1,2,3,4}
                             # columns in pipeline list

## Known shortcomings / bugs

- Uncollapsed state isn't maintained on page reload
- Pipeline groups currently selected with session cookie
- Missing installation & operation instructions and routines
- The stuff in the gocdmon subdirectory is not integrated yet

### Issues with cctray.xml

Some issues come from details in the cctray.xml file:

- For a build in progress, the timestamp is completion time for previous build. :-(
- Jobs aren't shown at all if they e.g. are to run on all machines.

## Deployment

Gocddash can be deployed with uWSGI, e.g. behind nginx.

To try out that thing work with uWSGI, you can initially run it like this:

cd to the directory where you have your app.py, and run:

    uwsgi --plugin python --http-socket 127.0.0.1:7777 -H <path to virtual env> -w app:app

Then you can point your browser to http://127.0.0.1:7777/dash and verify that
everything works as expected. When this works, you need to make sure that
everything also works with the uWSGI service and nginx.

Both these applications have similar setup strategies, with config under
/etc/uwsgi and /etc/nginx.

## Development

See the instructions in "README-analysis.md"
