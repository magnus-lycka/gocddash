from flask import Flask, render_template, request, make_response, redirect, url_for, Blueprint
import cctray_source
import parse_cctray
import getpass
import argparse
from collections import defaultdict
import json
from datetime import date, datetime

group_of_pipeline = defaultdict(str)

# Use a blueprint to allow URLs to be prefixed through
# APPLICATION_ROOT without running the app as a
# sub-mounted WSGI environment. See
# http://stackoverflow.com/questions/18967441/add-a-prefix-to-all-flask-routes
gocddash = Blueprint('gocddash', __name__)


def get_bootstrap_theme():
    theme = request.cookies.get('theme_cookie')
    return theme or 'cyborg'


def get_footer():
    try:
        return open('footer.txt').read()
    except IOError:
        return '???'


@gocddash.route("/", methods=['GET'])
def dashboard():
    which = request.args.get('which', 'failing')
    kwargs = {}
    if 'GO_SERVER_USER' in app.config:
        kwargs['auth'] = (app.config['GO_SERVER_USER'], app.config['GO_SERVER_PASSWD'])
    xml = cctray_source.get_cctray_source(
        app.config['GO_SERVER_URL'] + '/go/cctray.xml',
        **kwargs).data
    project = parse_cctray.Projects(xml)
    groups = request.cookies.get(
        'checked_pipeline_groups_cookie', '').split(',')
    pipelines = project.select(
        which, groups=groups, group_map=group_of_pipeline)
    return render_template('index.html',
                           go_server_url=app.config['PUBLIC_GO_SERVER_URL'],
                           pipelines=pipelines,
                           theme=get_bootstrap_theme(),
                           cols=app.config['PIPELINE_COLUMNS'],
                           now=datetime.now(),
                           footer=get_footer())


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


app = Flask(__name__)
app.config.from_pyfile('application.cfg', silent=False)
app.register_blueprint(gocddash, url_prefix=app.config["APPLICATION_ROOT"])


@app.template_filter('bootstrap_status')
def bootstrap_status(cctray_status):
    mapping = {
        'Failure': 'danger',
        'Building after Failure': 'warning',
        'Building after Success': 'info',
        'Success': 'success',
    }
    return mapping.get(cctray_status, 'default')


@app.template_filter('bootstrap_building')
def bootstrap_building(cctray_status):
    if 'Building' in cctray_status:
        return "progress-bar-striped"
    return ""


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


def get_all_pipeline_groups():
    kwargs = {}
    if 'GO_SERVER_USER' in app.config:
        kwargs['auth'] = (app.config['GO_SERVER_USER'], app.config['GO_SERVER_PASSWD'])
    json_text = cctray_source.get_cctray_source(
        app.config['GO_SERVER_URL'] + '/go/api/config/pipeline_groups',
        **kwargs).data
    full_json = json.loads(json_text)
    pipeline_groups = []
    for pipeline_group in full_json:
        pipeline_groups.append([pipeline_group['name'], '', []])
        for pipeline in pipeline_group['pipelines']:
            pipeline_groups[-1][-1].append(pipeline['name'])
            group_of_pipeline[pipeline['name']] = pipeline_group['name']
    return pipeline_groups


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--go-server-url', help='go server url')
    parser.add_argument('-u', '--go-server-user', help='go server user name')
    parser.add_argument('-p', '--go-server-passwd', help='go server password')
    parser.add_argument('-d', '--debug', action='store_true')
    parser.add_argument('-c', '--pipeline-columns', type=int, choices=[1, 2, 3, 4],
                        default=app.config['PIPELINE_COLUMNS'], help="# columns in pipeline list")
    pargs = parser.parse_args()
    pargs_dict = vars(pargs)
    app.config.update({key.upper(): pargs_dict[key] for key in pargs_dict if pargs_dict[key]})


if __name__ == "__main__":
    parse_args()
    if 'GO_SERVER_URL' not in app.config:
        app.config['GO_SERVER_URL'] = raw_input('go-server url: ')
    if 'GO_SERVER_USER' not in app.config:
        app.config['GO_SERVER_USER'] = raw_input('go-user: ')
    if 'GO_SERVER_PASSWD' not in app.config:
        app.config['GO_SERVER_PASSWD'] = getpass.getpass()
    app.run()
