import argparse
import getpass
import json
import os
import sys
from collections import defaultdict
from datetime import date, datetime
from inspect import getsourcefile
from os.path import abspath
from pathlib import Path

from flask import Flask, render_template, request, make_response, redirect, url_for, Blueprint, abort

sys.path.append(str(Path(abspath(getsourcefile(lambda: 0))).parents[1]))

from gocddash import parse_cctray
from gocddash.util.config import create_config
from gocddash.analysis.go_client import go_get_pipeline_groups, go_get_cctray, go_get_pipeline_status, create_go_client, get_client
from gocddash.console_parsers.git_blame_compare import get_git_comparison
from gocddash.dash_board import failure_tip, pipeline_status
from gocddash.analysis.data_access import get_connection, create_connection
from gocddash.analysis.domain import get_previous_stage, get_current_stage, get_latest_passing_stage

group_of_pipeline = defaultdict(str)

# Use a blueprint to allow URLs to be prefixed through
# APPLICATION_ROOT without running the app as a
# sub-mounted WSGI environment. See
# http://stackoverflow.com/questions/18967441/add-a-prefix-to-all-flask-routes
gocddash = Blueprint('gocddash', __name__)

def get_bootstrap_theme():
    theme = request.cookies.get('theme_cookie')
    return theme or 'paper'


def get_footer():
    try:
        return open('footer.txt').read()
    except IOError:
        return '???'


@gocddash.route("/", methods=['GET'])
def dashboard():
    which = request.args.get('which', 'failing')
    project = get_cctray_status()
    progress_bar_data = get_progress_bar_data(project)
    groups = request.cookies.get(
        'checked_pipeline_groups_cookie', '').split(',')
    pipelines = project.select(
        which, groups=groups, group_map=group_of_pipeline)
    for pipeline in pipelines:
        pipeline_name = pipeline.name
        message, whom = pipeline_is_paused(pipeline_name)
        if message:
            pipeline.status = 'Paused'
            pipeline.messages['PausedCause'].add(message)
        if whom:
            pipeline.messages['PausedBy'].add(whom)

    synced_pipelines = dict()
    for name, max_counter in get_connection().get_synced_pipelines():
        synced_pipelines[name] = max_counter

    return render_template('index.html',
                           go_server_url=app.config['PUBLIC_GO_SERVER_URL'],
                           pipelines=pipelines,
                           theme=get_bootstrap_theme(),
                           cols=app.config['PIPELINE_COLUMNS'],
                           now=datetime.now(),
                           footer=get_footer(),
                           synced_pipelines=synced_pipelines,
                           progress_bar_data=progress_bar_data,
                           application_root=app.config['APPLICATION_ROOT'])


def get_progress_bar_data(project):
    no_failing_pipelines = float(len(project.select("failing")))
    no_progress_pipelines = float(len(project.select("progress")))
    total_no_pipelines = float(len(project.select("all")))

    success_percentage = (total_no_pipelines - no_progress_pipelines) / total_no_pipelines * 100
    progress_percentage = (no_progress_pipelines - no_failing_pipelines) / total_no_pipelines * 100
    failing_percentage = no_failing_pipelines / total_no_pipelines * 100

    return [success_percentage, progress_percentage, failing_percentage]


def get_cctray_status():
    xml = go_get_cctray()
    project = parse_cctray.Projects(xml)
    return project


@gocddash.app_errorhandler(500)
def internal_server_error(e):
    return render_template('500.html', statuscode=e,), 500


@gocddash.app_errorhandler(404)
def page_not_found(e):
    return render_template('404.html', statuscode=e, dashboard_link=url_for('gocddash.dashboard')), 404

# Catches all errors - a bit too trigger happy
# @gocddash.app_errorhandler(Exception)
# def all_exception_handler(error):
#     return render_template('500.html', statuscode=error), 500


@gocddash.route("/select/", methods=['GET', 'POST'])
def select():
    all_pipeline_groups = get_all_pipeline_groups()
    # all_pipeline_groups is a list of
    # [ 'name', checked?, [pipelines names...] ]

    if request.method == 'POST':
        checked_pipeline_groups = list(request.form)
        response = redirect(url_for('gocddash.dashboard'), code=302)
        response.set_cookie('checked_pipeline_groups_cookie',
                            value=",".join(checked_pipeline_groups))
    else:
        checked_pipeline_groups = request.cookies.get(
            'checked_pipeline_groups_cookie', '').split(',')
        for i, pipeline_group in enumerate(all_pipeline_groups):
            if pipeline_group[0] in checked_pipeline_groups:
                all_pipeline_groups[i][1] = 'checked'
        template = render_template('select.html',
                                   go_server_url=app.config['PUBLIC_GO_SERVER_URL'],
                                   pipelinegroups=all_pipeline_groups,
                                   now=datetime.now(),
                                   theme=get_bootstrap_theme(),
                                   footer=get_footer())
        response = make_response(template)
    return response


@gocddash.route("/select_theme/", methods=['GET', 'POST'])
def select_theme():
    if request.method == 'POST':
        theme = request.form.get('theme_name')
        response = redirect(url_for('gocddash.select_theme'), code=302)
        response.set_cookie('theme_cookie',
                            value=theme or get_bootstrap_theme())
    else:
        template = render_template('select_theme.html',
                                   go_server_url=app.config['PUBLIC_GO_SERVER_URL'],
                                   now=datetime.now(),
                                   theme=get_bootstrap_theme(),
                                   footer=get_footer())
        response = make_response(template)
    return response


@gocddash.route("/insights/<pipelinename>", methods=['GET'])
def insights(pipelinename):
    current_stage = get_current_stage(pipelinename)
    if current_stage is None:
        abort(500, "Database error. Have you tried syncing some pipelines using sync_pipelines.py?")
    current_status = pipeline_status.create_stage_info(current_stage)
    last_stage = get_previous_stage(current_stage.pipeline_name, current_stage.pipeline_counter,
                                    current_stage.stage_index)
    previous_status = pipeline_status.create_stage_info(last_stage)
    latest_passing_stage = get_latest_passing_stage(pipelinename)

    if current_stage.is_success():
        git_blame_data = []
    else:
        git_blame_data = get_git_comparison(pipelinename, current_stage.pipeline_counter, latest_passing_stage.pipeline_counter)

    base_url = app.config['PUBLIC_GO_SERVER_URL']

    rerun_link = base_url + "pipelines/{}/{}/{}/{}".format(current_stage.pipeline_name,
                                                                          current_stage.pipeline_counter,
                                                                          current_stage.stage_name,
                                                                          current_stage.stage_index)
    log_link = base_url + "tab/build/detail/{}/{}/{}/{}/{}#tab-tests".format(
        current_stage.pipeline_name, current_stage.pipeline_counter, current_stage.stage_name,
        current_stage.stage_index, "defaultJob")

    main_pipeline_link = base_url + "tab/pipeline/history/{}".format(current_stage.pipeline_name)

    comparison_link = base_url + "compare/{}/{}/with/{}".format(current_stage.pipeline_name,
                                                                               current_stage.pipeline_counter,
                                                                               latest_passing_stage.pipeline_counter)

    dash_status = get_cctray_status()

    template = render_template(
        'insights.html',  # Defined in the templates folder
        go_server_url=app.config['PUBLIC_GO_SERVER_URL'],
        now=datetime.now(),
        theme=get_bootstrap_theme(),
        footer=get_footer(),
        pipeline_status=current_status,
        gitblame=git_blame_data,
        rerun_link=rerun_link,
        comparison_link=comparison_link,
        live_info=dash_status.pipelines[pipelinename],
        latest_passing_stage=latest_passing_stage,
        previous_status=previous_status,
        failure_tip=failure_tip.get_failure_tip(current_status, previous_status, latest_passing_stage.pipeline_counter),
        log_link=log_link,
        main_pipeline_link=main_pipeline_link
    )
    return make_response(template)


app = Flask(__name__)
app.config.from_pyfile('application.cfg', silent=False)
app.register_blueprint(gocddash, url_prefix=app.config["APPLICATION_ROOT"])
create_config()
create_connection(db_port=app.config['DB_PORT'])
create_go_client(app.config['GO_SERVER_URL'], (app.config['GO_SERVER_USER'], app.config['GO_SERVER_PASSWD']))


@app.template_filter('bootstrap_status')
def bootstrap_status(cctray_status):
    mapping = {
        'Failure': 'danger',
        'Building after Failure': 'warning',
        'Building after Success': 'info',
        'Success': 'success',
        'Paused': 'default',
    }
    return mapping.get(cctray_status, 'default')


@app.template_filter('rerun_valid')
def rerun_valid(rerun_status):
    if 'Building' in rerun_status:
        return "btn btn-lg btn-block"
    return "btn btn-primary btn-lg btn-block"


@app.template_filter('bootstrap_building')
def bootstrap_building(cctray_status):
    if 'Building' in cctray_status:
        return "progress-bar-striped"
    return ""


@app.template_filter('build_outcome')
def build_outcome(build_passed):
    return "text-success" if build_passed else "text-danger"


@app.template_filter('failure_stage')
def failure_stage(failure_stage):
    return "text-danger" if failure_stage else "text-warning"


@app.template_filter('building_panel_label')
def building_panel_label(cctray_status):
    if 'Building' in cctray_status:
        return "Building in Go"
    return "Latest in Go"


@app.template_filter('pluralize')
def pluralize(number, singular='', plural='s'):
    if number == 1:
        return singular
    else:
        return plural


@app.template_filter('time_or_date')
def time_or_date(timestamp):
    date_part, time_part = timestamp.split('T')
    if date_part == str(date.today()):
        return time_part
    return date_part


@app.template_filter('dt')
def _jinja2_filter_datetime(date_, fmt=None):
    if fmt:
        return date_.strftime(fmt)
    else:
        return date_.strftime('%Y-%m-%d')


@app.template_filter('tm')
def _jinja2_filter_datetime(datetime_, fmt=None):
    if fmt:
        return datetime_.strftime(fmt)
    else:
        return datetime_.strftime('%H:%M:%S')


@app.before_request
def setup():
    get_all_pipeline_groups()


def pipeline_is_paused(pipeline_name):
    kwargs = {}
    if 'GO_SERVER_USER' in app.config:
        response = go_get_pipeline_status(pipeline_name)
        # status = json.loads(response.text.replace("\\'", ""))
        status = json.loads(response)
        if status["paused"]:
            return status.get("pausedCause") or 'Paused', status.get("pausedBy")
    return None, None


def get_all_pipeline_groups():
    kwargs = {}
    if 'GO_SERVER_USER' in app.config:
        kwargs['auth'] = (app.config['GO_SERVER_USER'], app.config['GO_SERVER_PASSWD'])
    json_text = go_get_pipeline_groups()
    full_json = json.loads(json_text)
    pipeline_groups = []
    for pipeline_group in full_json:
        pipeline_groups.append([pipeline_group['name'], '', []])
        for pipeline in pipeline_group['pipelines']:
            pipeline_groups[-1][-1].append(pipeline['name'])
            group_of_pipeline[pipeline['name']] = pipeline_group['name']
    return pipeline_groups


#
def is_valid_file(parser, arg):
    if not os.path.isfile(arg):
        parser.error("The file %s does not exist!" % arg)
    else:
        return open(arg, 'r')  # return an open file handle


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--go-server-url', help='go server url')
    parser.add_argument('-u', '--go-server-user', help='go server user name')
    parser.add_argument('-p', '--go-server-passwd', help='go server password')
    parser.add_argument('-d', '--debug', action='store_true')
    parser.add_argument('-c', '--pipeline-columns', type=int, choices=[1, 2, 3, 4],
                        default=app.config['PIPELINE_COLUMNS'], help="# columns in pipeline list")
    parser.add_argument('-b', '--bind-port', help='bind port')
    parser.add_argument('--db-port', help='database port')
    parser.add_argument('--pipeline-config', help='pipeline config')
    parser.add_argument('--file-client', help='file client')
    pargs = parser.parse_args()
    pargs_dict = vars(pargs)
    app.config.update({key.upper(): pargs_dict[key] for key in pargs_dict if pargs_dict[key]})
    return pargs_dict

def main():
    if not os.path.isfile(os.path.dirname(abspath(getsourcefile(lambda: 0))) + '/application.cfg'):
        print("Error: Missing application.cfg file in {}/".format(os.path.dirname((abspath(getsourcefile(lambda: 0))))))
        quit()
    pargs_dict = parse_args()
    if 'GO_SERVER_URL' not in app.config:
        app.config['GO_SERVER_URL'] = input('go-server url: ')
    if 'GO_SERVER_USER' not in app.config:
        app.config['GO_SERVER_USER'] = input('go-user: ')
    if 'GO_SERVER_PASSWD' not in app.config:
        app.config['GO_SERVER_PASSWD'] = getpass.getpass()

    if pargs_dict['file_client']:
        create_go_client(pargs_dict['file_client'], auth=None)
    pipeline_path = pargs_dict['pipeline_config']
    if pipeline_path:
        if os.path.isfile(pargs_dict['pipeline_config']):
            create_config(pargs_dict['pipeline_config'])

    app.run(port=app.config['BIND_PORT'])

if __name__ == "__main__":
    main()
