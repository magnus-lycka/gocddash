Developing GOCD Dashboard
=========================

Before everything:

With pip3 (apt-get install python3-pip), install the following packages:

flask
jinja2
psycopg2
pandas
yoyo-migrations
beautifulsoup4
bokeh

(Don't be afraid if the pandas installation takes a while.)

Start up a local database with docker:

    docker run -p 15554:5432 -d go-analysis-db:1.1.1-GO

(The image will be put on docker hub shortly. It's just an empty postgresql 9.3 database with a default schema and user 'analysisappluser')

Run the migration script

    yoyo apply --database postgresql://analysisappluser:analysisappluser@localhost:15554/go-analysis -b

Use ./sync_pipelines.py ('-d' for continuous sync) to fetch data for the pipelines specified in pipelines.json.

Stage failures will be parsed and categorized in the following three distinct phases in which the failure occurred:

* STARTUP: the job failed but the tests were not even started, no tests run according to JUnit
* TEST: there were test failures according to JUnit
* POST: all tests passed according to JUnit, but the job still failed

For the runs that actually contain _test_ failures, additional information is gathered, which is then used for analysis:

* Which tests failed, and how?


Starting the Dashboard
-----------------------

Before it will work you need some configuration. Create a file 'application.cfg' under 'gocddash'. There is a sample example file there named 'application.cfg.example' that you can copy.

The synchronization of run data from Go is done through `sync_pipelines.py`. Synchronization of data will be done for pipelines specified in `pipelines.json`. Look at `pipelines.json.example` to see what format this file should have.

Run `app.py` in the gocddash directory - this will serve the dashboard.

The dashboard is available locally from http://127.0.0.1:5000/dash/
1. Since by default no pipelines are shown, they must be enabled under "Select pipeline groups".
2. Once data has been synchronized, pipelines (under the Failing/Progress/All tabs) with additional information are marked with "Insights" along with the latest pipeline count for which the information pertains to.
3. On the Insights page for a pipeline, information is displayed in three panels. Failed pipelines contain more information and actions.
4. On the Pipeline graphs page, success rate/failure type per agent and historical test count graphs are available.
5. A graph of system wide historical success rate per agent is also available through the More/Config dropdown menu at the top.
6. The sync process also handles an email notification system for alerting primary suspects when a pipeline breaks. The notification system is opt-in per pipeline as specified in pipelines.json.