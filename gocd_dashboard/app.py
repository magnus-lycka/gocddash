from flask import Flask, render_template, request, make_response
import cctray_source
import parse_cctray
import getpass
import argparse
from collections import defaultdict
import json
from datetime import date

config = defaultdict(str)
group_of_pipeline = defaultdict(str)

app = Flask(__name__)


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


@app.route("/", methods=['GET'])
def dashboard():
    which = request.args.get('which', 'failing')
    xml = cctray_source.get_cctray_source(
        config['server'] + '/go/cctray.xml',
        auth=(config['user'], config['passwd'])).data
    project = parse_cctray.Projects(xml)
    groups = request.cookies.get('checked_pipeline_groups_cookie', '').split(',')
    pipelines = project.select(which, groups=groups, group_map=group_of_pipeline)
    return render_template('index.html', pipelines=pipelines, cols=config['columns'])


@app.before_first_request
def setup():
    get_all_pipeline_groups()


def get_all_pipeline_groups():
    json_text = cctray_source.get_cctray_source(
        config['server'] + '/go/api/config/pipeline_groups',
        auth=(config['user'], config['passwd'])).data
    full_json = json.loads(json_text)
    pipeline_groups = []
    for pipeline_group in full_json:
        pipeline_groups.append([pipeline_group['name'], '', []])
        for pipeline in pipeline_group['pipelines']:
            pipeline_groups[-1][-1].append(pipeline['name'])
            group_of_pipeline[pipeline['name']] = pipeline_group['name']
    return pipeline_groups


@app.route("/select", methods=['GET', 'POST'])
def select():
    all_pipeline_groups = get_all_pipeline_groups()
    # all_pipeline_groups is a list of
    # [ 'name', checked?, [piplines names...] ]

    blob = ''
    if request.method == 'POST':
        checked_pipeline_groups = list(request.form)
    else:
        checked_pipeline_groups = request.cookies.get('checked_pipeline_groups_cookie', '').split(',')
    for i, pipeline_group in enumerate(all_pipeline_groups):
        if pipeline_group[0] in checked_pipeline_groups:
            all_pipeline_groups[i][1] = 'checked'
    template = render_template('select.html', blob=blob, pipelinegroups=all_pipeline_groups)
    response = make_response(template)
    response.set_cookie('checked_pipeline_groups_cookie', value=",".join(checked_pipeline_groups))
    return response


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--server', help='go server url')
    parser.add_argument('-u', '--user', help='go server user name')
    parser.add_argument('-p', '--passwd', help='go server password')
    parser.add_argument('-d', '--debug', action='store_true')
    parser.add_argument('-c', '--columns', type=int, choices=[1, 2, 3, 4], default=2, help="# columns in pipeline list")
    pargs = parser.parse_args()
    config.update(vars(pargs))


if __name__ == "__main__":
    parse_args()
    if not config['server']:
        config['server'] = raw_input('go-server url: ')
    if not config['user']:
        config['user'] = raw_input('user: ')
    if not config['passwd']:
        config['passwd'] = getpass.getpass()
    app.run(debug=config['debug'])
