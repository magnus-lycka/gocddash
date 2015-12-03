# gocd-dashboard
Status dashboard for Go.CD Continuous Delivery Server

Gocd-dashboard provides an overview of the builds in your
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

Gocd-dashboard uses the cctray.xml file from the go-server.

Since gocd-dashboard uses bootstrap, you can easily pimp
it to your liking.

## Usage

   usage: app.py [-h] [-s SERVER] [-u USER] [-p PASSWD] [-d] [-c {1,2,3,4}]

   optional arguments:
     -h, --help            show this help message and exit
     -s SERVER, --server SERVER
                           go server url
     -u USER, --user USER  go server user name
     -p PASSWD, --passwd PASSWD
                           go server password
     -d, --debug
     -c {1,2,3,4}, --columns {1,2,3,4}
                           # columns in pipeline list

## Known shortcomings / bugs

- You need to press a save button after selecting/deselecting
  pipeline-groups, and then go back to the main page.
- The "Select all groups" button only works once. (Then you need to save etc.)
- Uncollapsed state isn't maintained on page reload
- No change of glypgh on changing collapsed state
- Pipeline groups currently selected with session cookie
- Missing installation & operation instructions and routines
- The stuff in the gocdmon subdirectory is not integrated yet

### Issues with cctray.xml

Some issues come from details in the cctray.xml file:

- It's unclear to me what the timedtamp refers to for a build in progress.
- Jobs aren't shown at all if they e.g. are to run on all machines.

