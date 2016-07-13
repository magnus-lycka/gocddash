GO Analysis
===========

Before everything:

With pip3 (apt-get install python3-pip), install the following packages:

flask
jinja2
psycopg2
htmlparser
pandas
yoyo-migrations

(Don't be afraid if the pandas installation takes a while.)

Start up a local database with docker:

    docker run -p 15554:5432 -d dockerregistry.pagero.local/go-analysis-db:1.1.1-GO

Run the migration script

    yoyo apply --database postgresql://analysisappluser:analysisappluser@localhost:15554/go-analysis

Usage for the cli:

    ./go_cli.py [pull|info|export] [-p PIPELINE] [-d] [-n PULL_COUNT] [-s START_COUNTER] [-f FILENAME]

Modes:

`info` lists metadata of the current state of the client database of the selected pipeline.

`pull` synchronizes run information from GO into the client database.
With only the `-n` flag, it synchronizes the input number of runs beginning from the last synchronized run.
With both the `-s` and `-n` flags, it is possible to set the start run number, synchronizing the specified consecutive number of runs.


Test log analysis is configured for the output format of texttest - but other formats could be included.
The first consideration is during which part of the test run the test failed - split in three categories:

* STARTUP: runDeployer did not finish
* TEST: there were test failures according to JUnit
* POST: all tests passed according to JUnit, but the process still returned an error code (meaning that post-test Git operation failed)

For the runs that actually contain _test_ failures, additional information is gathered, which is then used for analysis:

* Which index did the failing test(s) have?
* Which documents were missing/new/differences


Non-comprehensive list of indicators for flickering tests:

* Green-red-green consecutive
* Red-green in consecutive stages
* First test in suite fails


Dashboard:
----------
Run `main.py` - this will serve the dashboard.
The synchronization of run data from Go is done through `sync_pipelines.py`. Synchronization of data will be done for pipelines specified in `pipelines.json`.

The dashboard is available locally from http://127.0.0.1:5000/dash/
1. Since by default no pipelines are shown, they must be enabled under "Select pipeline groups".
2. Once data has been synchronized, pipelines (under the Failing/Progress/All tabs) with additional information are marked with "Insights available" along with the latest pipeline count for which the information pertains to.
3. On the insights page for a pipeline, information is displayed in three panels. Failed pipelines contain more information and actions.